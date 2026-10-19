// Supermarket Voice Navigator - Frontend JavaScript

class VoiceNavigatorApp {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.speechSynthesis = window.speechSynthesis;
        this.settings = {
            voiceSpeed: 1.0,
            voiceVolume: 0.8,
            autoSpeak: true,
            highContrast: false
        };

        // Initialize the application
        this.init();
    }

    async init() {
        // Load settings from localStorage
        this.loadSettings();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initialize speech recognition
        this.initSpeechRecognition();
        
        // Load initial data
        await this.loadInitialData();
        
        // Apply settings
        this.applySettings();
        
        console.log('Voice Navigator App initialized');
    }

    setupEventListeners() {
        // Voice button
        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleVoiceRecognition());
        }
        
        // Voice stop button
        const stopVoiceBtn = document.getElementById('stop-voice-btn');
        if (stopVoiceBtn) {
            stopVoiceBtn.addEventListener('click', () => this.stopVoiceRecognition());
        }

        // Text input
        const textSubmit = document.getElementById('text-submit');
        const textCommand = document.getElementById('text-command');
        
        if (textSubmit) {
            textSubmit.addEventListener('click', () => this.handleTextCommand());
        }
        
        if (textCommand) {
            textCommand.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleTextCommand();
                }
            });
        }

        // Quick action buttons
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const command = e.currentTarget.dataset.command;
                if (command) {
                    this.processCommand(command);
                }
            });
        });

        // Product search
        const searchBtn = document.getElementById('search-btn');
        const productSearch = document.getElementById('product-search');
        
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.handleProductSearch());
        }
        
        if (productSearch) {
            productSearch.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleProductSearch();
                }
            });
            
            // Live search as user types
            let searchTimeout;
            productSearch.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    if (e.target.value.length > 2) {
                        this.searchProducts(e.target.value);
                    }
                }, 300);
            });
        }

        // Navigation controls
        const getDirectionsBtn = document.getElementById('get-directions');
        if (getDirectionsBtn) {
            getDirectionsBtn.addEventListener('click', () => this.handleGetDirections());
        }
        
        // Advanced navigation controls
        const getAdvancedDirectionsBtn = document.getElementById('get-advanced-directions');
        if (getAdvancedDirectionsBtn) {
            getAdvancedDirectionsBtn.addEventListener('click', () => this.handleAdvancedDirections());
        }
        
        // Update location control
        const updateLocationBtn = document.getElementById('update-location');
        if (updateLocationBtn) {
            updateLocationBtn.addEventListener('click', () => this.handleUpdateLocation());
        }

        // Speak response button
        const speakResponseBtn = document.getElementById('speak-response');
        if (speakResponseBtn) {
            speakResponseBtn.addEventListener('click', () => this.speakCurrentResponse());
        }
        
        // Stop speaking button
        const stopSpeakingBtn = document.getElementById('stop-speaking');
        if (stopSpeakingBtn) {
            stopSpeakingBtn.addEventListener('click', () => this.stopSpeaking());
        }

        // Settings modal
        const settingsBtn = document.getElementById('settings-btn');
        const settingsModal = document.getElementById('settings-modal');
        const saveSettingsBtn = document.getElementById('save-settings');
        
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.openSettings());
        }
        
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        }

        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => this.closeModal());
        });

        // Fullscreen toggle
        const fullscreenBtn = document.getElementById('fullscreen-btn');
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F11') {
                e.preventDefault();
                this.toggleFullscreen();
            }
            
            if (e.key === ' ' && e.ctrlKey) {
                e.preventDefault();
                this.toggleVoiceRecognition();
            }
        });
    }

    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                this.isListening = true;
                this.updateVoiceUI();
                this.updateStatus('🎤 Listening...');
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.updateStatus('Processing...');
                this.processCommand(transcript);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isListening = false;
                this.updateVoiceUI();
                this.updateStatus('❌ Speech recognition error');
                this.showToast('Speech recognition error: ' + event.error, 'error');
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.updateVoiceUI();
                this.updateStatus('🎤 Ready to listen');
            };
        } else {
            console.warn('Speech recognition not supported');
            this.showToast('Speech recognition not supported in this browser', 'warning');
        }
    }

    async loadInitialData() {
        try {
            // Load store map
            await this.loadStoreMap();
            
            // Load products and populate destination select
            await this.loadProducts();
            
            // Update current location
            await this.updateCurrentLocation();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showToast('Error loading store data', 'error');
        }
    }

    async loadStoreMap() {
        try {
            const response = await fetch('/api/get_store_map');
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.renderStoreMap(data);
            this.populateDestinations(data.landmarks, data.aisles);
            
        } catch (error) {
            console.error('Error loading store map:', error);
            throw error;
        }
    }

    async loadProducts() {
        try {
            const response = await fetch('/api/get_products');
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.products = data.products;
            this.categories = data.categories;
            
        } catch (error) {
            console.error('Error loading products:', error);
            throw error;
        }
    }

    async updateCurrentLocation() {
        try {
            const response = await fetch('/api/session_info');
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.updateLocationDisplay(data.current_location);
            
            // Store current location data for map
            const locationName = data.current_location.split(':')[0].trim();
            if (this.mapData && this.mapData.landmarks[locationName]) {
                this.currentLocationData = this.mapData.landmarks[locationName];
            } else {
                // Default to entrance if not found
                this.currentLocationData = { x: 0, y: 0, name: locationName };
            }
            
        } catch (error) {
            console.error('Error updating location:', error);
        }
    }

    toggleVoiceRecognition() {
        if (!this.recognition) {
            this.showToast('Speech recognition not available', 'error');
            return;
        }

        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }
    
    stopVoiceRecognition() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
            this.updateVoiceUI();
            this.showToast('Voice recognition stopped', 'info');
        }
    }

    handleTextCommand() {
        const textCommand = document.getElementById('text-command');
        const command = textCommand.value.trim();
        
        if (command) {
            textCommand.value = '';
            this.processCommand(command);
        }
    }

    async processCommand(command) {
        try {
            this.showLoading(true);
            this.updateStatus('Processing command...');
            
            const response = await fetch('/api/process_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Display response
            this.displayResponse(data.response);
            
            // Update location if changed
            this.updateLocationDisplay(data.current_location);
            
            // Check if server provided destination coordinates
            if (data.destination) {
                const destination = data.destination.name;
                const destCoords = { x: data.destination.x, y: data.destination.y };
                
                // Store destination coordinates for direct use
                if (!this.destinationCoords) {
                    this.destinationCoords = {};
                }
                this.destinationCoords[destination] = destCoords;
                
                // Determine starting point
                const startPoint = this.lastDestination || this.currentLocationName || 'Entrance';
                
                // Show navigation on map from last position to new destination
                this.showNavigationPath(startPoint, destination);
                
                // Update last destination for next navigation
                this.lastDestination = destination;
                
                // Update visual current location to show we're navigating there
                this.updateNavigationStatus(startPoint, destination);
                
                // Scroll to map
                this.scrollToMap();
                
                this.showLocationUpdateNotification(data.current_location);
            }
            
            // Auto-speak if enabled
            if (this.settings.autoSpeak) {
                this.speak(data.response);
            }
            
            this.updateStatus('✅ Command processed');
            
        } catch (error) {
            console.error('Error processing command:', error);
            this.displayResponse('Sorry, there was an error processing your command.');
            this.showToast('Error: ' + error.message, 'error');
            this.updateStatus('❌ Error processing command');
        } finally {
            this.showLoading(false);
        }
    }
    
    extractDestinationFromCommand(command, response) {
        // Try to extract destination from command or response
        const command_lower = command.toLowerCase();
        
        // Check if mapData is loaded
        if (!this.mapData) return null;
        
        // Get all possible locations
        const allLocations = [
            ...Object.keys(this.mapData.landmarks || {}),
            ...Object.keys(this.mapData.aisles || {})
        ];
        
        // Find matching location in command
        for (const location of allLocations) {
            if (command_lower.includes(location.toLowerCase())) {
                return location;
            }
        }
        
        // Try to extract from response (e.g., "located in Aisle 3")
        const aisleMatch = response.match(/Aisle \d+/i);
        if (aisleMatch) {
            return aisleMatch[0];
        }
        
        // Try to find section names
        const sectionMatch = response.match(/(Bakery|Dairy|Deli|Produce|Pharmacy|Household|Pet Care|Baby Care)/i);
        if (sectionMatch) {
            return sectionMatch[0];
        }
        
        return null;
    }
    
    scrollToMap() {
        const mapSection = document.querySelector('.store-map');
        if (mapSection) {
            mapSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    updateNavigationStatus(from, to) {
        // Update the status display to show navigation
        const locationElement = document.getElementById('current-location');
        if (locationElement) {
            locationElement.innerHTML = `📍 ${from} <span style="color: var(--primary-color);"> → ${to}</span>`;
        }
        
        // Show notification
        this.showToast(`Navigating: ${from} → ${to}`, 'success');
    }

    async handleProductSearch() {
        const searchInput = document.getElementById('product-search');
        const query = searchInput.value.trim();
        
        if (query) {
            await this.searchProducts(query);
        }
    }

    async searchProducts(query) {
        try {
            const response = await fetch(`/api/search_products?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.displaySearchResults(data.results);
            
        } catch (error) {
            console.error('Error searching products:', error);
            this.showToast('Error searching products', 'error');
        }
    }

    async handleGetDirections() {
        const select = document.getElementById('destination-select');
        const destination = select.value;
        
        if (!destination) {
            this.showToast('Please select a destination', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`/api/get_directions?destination=${encodeURIComponent(destination)}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.displayDirections(data.directions);
            
            // Show navigation path on map
            this.showNavigationPath(this.currentLocationName, destination);
            
            if (this.settings.autoSpeak) {
                this.speak(data.directions);
            }
            
        } catch (error) {
            console.error('Error getting directions:', error);
            this.showToast('Error getting directions', 'error');
        }
    }

    displayResponse(text) {
        const responseElement = document.getElementById('response-text');
        if (responseElement) {
            responseElement.textContent = text;
            this.currentResponse = text;
        }
    }

    displaySearchResults(results) {
        const container = document.getElementById('search-results');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (results.length === 0) {
            container.innerHTML = '<p>No products found</p>';
            return;
        }
        
        results.forEach(product => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.innerHTML = `
                <div class="result-name">${product.name}</div>
                <div class="result-details">${product.category} - ${product.aisle}</div>
            `;
            
            item.addEventListener('click', () => {
                this.processCommand(`find ${product.name}`);
            });
            
            container.appendChild(item);
        });
    }

    displayDirections(directions) {
        const container = document.getElementById('directions-display');
        if (container) {
            // Format the directions for better display
            container.innerHTML = this.formatDirections(directions);
        }
    }
    
    formatDirections(directions) {
        if (!directions) return '';
        
        // Convert emoji-formatted directions to HTML
        return directions
            .replace(/🎯/g, '<span class="direction-icon">🎯</span>')
            .replace(/🏁/g, '<span class="direction-icon">🏁</span>')
            .replace(/🧭/g, '<span class="direction-icon">🧭</span>')
            .replace(/📏/g, '<span class="direction-icon">📏</span>')
            .replace(/🛤️/g, '<span class="direction-icon">🛤️</span>')
            .replace(/👀/g, '<span class="direction-icon">👀</span>')
            .replace(/✅/g, '<span class="direction-icon">✅</span>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    renderStoreMap(mapData) {
        const gridContainer = document.getElementById('store-grid');
        const mapElement = document.getElementById('store-map');
        if (!gridContainer || !mapElement) return;
        
        // Store map data for later use
        this.mapData = mapData;
        this.currentPath = null;
        this.gridSize = { cols: 12, rows: 10 };
        
        // Clear existing elements
        gridContainer.innerHTML = '';
        
        // Remove existing aisles and path
        mapElement.querySelectorAll('.map-aisle, .navigation-path').forEach(el => el.remove());
        
        // Render aisle rectangles
        this.renderAisles(mapData);
        
        // Render markers for locations
        this.renderMapMarkers(mapData, this.gridSize);
        
        // Setup stop button
        this.setupStopButton();
    }
    
    renderAisles(mapData) {
        const mapElement = document.getElementById('store-map');
        const gridContainer = document.getElementById('store-grid');
        if (!mapElement || !gridContainer) return;
        
        // Define aisle positions based on store layout
        // Format: { name, x, y, width, height } (x: 0-100, y: 0-60)
        const aisleDefinitions = [
            // Main vertical aisles
            { name: 'Aisle 1', x: 15, y: 15, width: 8, height: 30 },
            { name: 'Aisle 2', x: 28, y: 15, width: 8, height: 30 },
            { name: 'Aisle 3', x: 41, y: 15, width: 8, height: 30 },
            { name: 'Aisle 4', x: 54, y: 15, width: 8, height: 30 },
            { name: 'Aisle 5', x: 67, y: 15, width: 8, height: 30 },
            // Special sections
            { name: 'Produce', x: 80, y: 6, width: 15, height: 18 },
            { name: 'Dairy', x: 80, y: 27, width: 15, height: 12 },
            { name: 'Bakery', x: 55, y: 3, width: 20, height: 9 },
            { name: 'Deli', x: 25, y: 3, width: 20, height: 9 },
            { name: 'Household', x: 80, y: 42, width: 15, height: 12 },
            { name: 'Baby Care', x: 15, y: 48, width: 15, height: 9 },
            { name: 'Pet Care', x: 35, y: 48, width: 15, height: 9 },
        ];
        
        const gridRect = gridContainer.getBoundingClientRect();
        const mapRect = mapElement.getBoundingClientRect();
        const gridOffsetLeft = gridContainer.offsetLeft;
        const gridOffsetTop = gridContainer.offsetTop;
        
        aisleDefinitions.forEach(aisle => {
            const aisleEl = document.createElement('div');
            aisleEl.className = 'map-aisle';
            aisleEl.dataset.aisle = aisle.name;
            
            // Calculate position (x uses 0-100 scale, y uses 0-60 scale)
            const left = gridOffsetLeft + (aisle.x / 100) * gridContainer.offsetWidth;
            const top = gridOffsetTop + (aisle.y / 60) * gridContainer.offsetHeight;
            const width = (aisle.width / 100) * gridContainer.offsetWidth;
            const height = (aisle.height / 60) * gridContainer.offsetHeight;
            
            aisleEl.style.left = left + 'px';
            aisleEl.style.top = top + 'px';
            aisleEl.style.width = width + 'px';
            aisleEl.style.height = height + 'px';
            
            // Add label
            const label = document.createElement('span');
            label.className = 'aisle-label';
            label.textContent = aisle.name;
            aisleEl.appendChild(label);
            
            // Click handler to navigate
            aisleEl.addEventListener('click', () => {
                this.processCommand(`go to ${aisle.name}`);
            });
            
            mapElement.appendChild(aisleEl);
        });
        
        // Store aisle definitions for path calculations
        this.aisleDefinitions = aisleDefinitions;
    }
    
    renderMapMarkers(mapData, gridSize) {
        const mapElement = document.getElementById('store-map');
        const gridContainer = document.getElementById('store-grid');
        if (!mapElement || !gridContainer) return;
        
        // Remove existing markers
        mapElement.querySelectorAll('.map-marker').forEach(marker => marker.remove());
        
        // Determine current display location
        let currentDisplayLocation = this.currentLocationData || mapData.current_location;
        let currentDisplayName = this.currentLocationName || 'Entrance';
        
        if (this.lastDestination && this.mapData) {
            const destLocation = this.mapData.landmarks[this.lastDestination] || 
                                this.getAisleLocation(this.lastDestination);
            if (destLocation) {
                currentDisplayLocation = destLocation;
                currentDisplayName = this.lastDestination;
            }
        }
        
        // Render current location marker
        if (currentDisplayLocation) {
            const marker = this.createMarker(
                currentDisplayLocation.x || 5,
                currentDisplayLocation.y || 5,
                'current-location',
                '📍',
                currentDisplayName || 'You are here',
                gridSize,
                true  // Show "You are here" label
            );
            this.currentMarker = marker;
        }
        
        // Render landmark markers (excluding current position)
        Object.entries(mapData.landmarks).forEach(([name, location]) => {
            if (name !== currentDisplayName && name !== this.lastDestination) {
                this.createMarker(
                    location.x,
                    location.y,
                    'landmark',
                    '📌',
                    name,
                    gridSize
                );
            }
        });
    }
    
    getAisleLocation(aisleName) {
        // Get center position of an aisle for marker placement
        if (!this.aisleDefinitions) return null;
        
        const aisle = this.aisleDefinitions.find(a => 
            a.name.toLowerCase() === aisleName.toLowerCase()
        );
        
        if (aisle) {
            return {
                x: aisle.x + aisle.width / 2,
                y: aisle.y + aisle.height / 2,
                name: aisle.name
            };
        }
        return null;
    }
    
    createMarker(x, y, type, icon, label, gridSize, showLabel = false) {
        const mapElement = document.getElementById('store-map');
        const gridContainer = document.getElementById('store-grid');
        if (!mapElement || !gridContainer) return null;
        
        const marker = document.createElement('div');
        marker.className = `map-marker ${type}`;
        marker.innerHTML = icon;
        marker.dataset.name = label;
        
        // For current location, add permanent "You are here" label
        if (showLabel && type === 'current-location') {
            const permLabel = document.createElement('div');
            permLabel.className = 'current-location-label';
            permLabel.textContent = 'You are here';
            marker.appendChild(permLabel);
        }
        
        // Create hover label
        const labelDiv = document.createElement('div');
        labelDiv.className = 'map-marker-label';
        labelDiv.textContent = label;
        marker.appendChild(labelDiv);
        
        // Calculate position
        const gridOffsetLeft = gridContainer.offsetLeft;
        const gridOffsetTop = gridContainer.offsetTop;
        const normalizedX = gridOffsetLeft + (x / 100) * gridContainer.offsetWidth;
        const normalizedY = gridOffsetTop + (y / 60) * gridContainer.offsetHeight;
        
        marker.style.left = normalizedX + 'px';
        marker.style.top = normalizedY + 'px';
        
        // Click handler for markers
        marker.addEventListener('click', () => {
            if (type === 'landmark') {
                this.processCommand(`go to ${label}`);
            }
        });
        
        mapElement.appendChild(marker);
        
        return marker;
    }
    
    showNavigationPath(fromLocation, toLocation) {
        const gridContainer = document.getElementById('store-grid');
        const mapDisplay = document.getElementById('store-map');
        if (!gridContainer || !mapDisplay) return;
        
        // Clear existing path
        this.clearNavigationPath();
        
        // Add active navigation class to map
        mapDisplay.classList.add('active-navigation');
        
        // Get start and end positions
        const startPos = this.getLocationPosition(fromLocation);
        const endPos = this.getLocationPosition(toLocation);
        
        if (!startPos || !endPos) {
            console.warn('Could not find positions for navigation');
            return;
        }
        
        // Create destination marker
        const destMarker = this.createMarker(
            endPos.x,
            endPos.y,
            'destination',
            '🎯',
            toLocation,
            this.gridSize || { cols: 12, rows: 10 }
        );
        
        // Draw SVG path
        this.drawNavigationPath(startPos, endPos);
        
        // Animate current location marker moving to destination
        this.animateMovement(startPos, endPos, toLocation);
        
        // Show stop button
        const stopBtn = document.getElementById('stop-navigation');
        if (stopBtn) {
            stopBtn.style.display = 'flex';
        }
        
        // Show reset button
        const resetBtn = document.getElementById('reset-navigation');
        if (resetBtn) {
            resetBtn.style.display = 'flex';
        }
        
        // Show toast notification
        this.showToast(`🗺️ Navigating: ${fromLocation} → ${toLocation}`, 'success');
    }
    
    getLocationPosition(locationName) {
        if (!this.mapData) return null;
        
        // First check if we have stored coordinates from server
        if (this.destinationCoords && this.destinationCoords[locationName]) {
            return this.destinationCoords[locationName];
        }
        
        // Check landmarks
        const landmark = this.mapData.landmarks[locationName];
        if (landmark) {
            return { x: landmark.x, y: landmark.y };
        }
        
        // Check aisles
        const aisle = this.mapData.aisles[locationName];
        if (aisle && aisle.path && aisle.path.length > 0) {
            return { x: aisle.path[0].x, y: aisle.path[0].y };
        }
        
        // Check custom aisle definitions
        const aislePos = this.getAisleLocation(locationName);
        if (aislePos) {
            return { x: aislePos.x, y: aislePos.y };
        }
        
        // Default to entrance
        if (locationName.toLowerCase() === 'entrance' || !locationName) {
            return { x: 5, y: 5 };
        }
        
        return null;
    }
    
    drawNavigationPath(startPos, endPos) {
        const mapElement = document.getElementById('store-map');
        const gridContainer = document.getElementById('store-grid');
        if (!mapElement || !gridContainer) return;
        
        // Remove existing path
        mapElement.querySelectorAll('.navigation-path').forEach(el => el.remove());
        
        // Create SVG element
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.classList.add('navigation-path');
        svg.style.position = 'absolute';
        svg.style.top = '0';
        svg.style.left = '0';
        svg.style.width = '100%';
        svg.style.height = '100%';
        svg.style.pointerEvents = 'none';
        svg.style.zIndex = '5';
        
        // Calculate pixel positions
        const gridOffsetLeft = gridContainer.offsetLeft;
        const gridOffsetTop = gridContainer.offsetTop;
        
        const startX = gridOffsetLeft + (startPos.x / 100) * gridContainer.offsetWidth;
        const startY = gridOffsetTop + (startPos.y / 60) * gridContainer.offsetHeight;
        const endX = gridOffsetLeft + (endPos.x / 100) * gridContainer.offsetWidth;
        const endY = gridOffsetTop + (endPos.y / 60) * gridContainer.offsetHeight;
        
        // Create a curved path with waypoints
        const midX = (startX + endX) / 2;
        const midY = (startY + endY) / 2;
        
        // Create path with bezier curve
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        
        // Simple L-shaped path for better visibility
        let d;
        if (Math.abs(endX - startX) > Math.abs(endY - startY)) {
            // Go horizontal first, then vertical
            d = `M ${startX} ${startY} L ${endX} ${startY} L ${endX} ${endY}`;
        } else {
            // Go vertical first, then horizontal
            d = `M ${startX} ${startY} L ${startX} ${endY} L ${endX} ${endY}`;
        }
        
        path.setAttribute('d', d);
        path.setAttribute('stroke', '#60a5fa');
        path.setAttribute('stroke-width', '4');
        path.setAttribute('stroke-dasharray', '12, 6');
        path.setAttribute('stroke-linecap', 'round');
        path.setAttribute('stroke-linejoin', 'round');
        path.setAttribute('fill', 'none');
        path.style.animation = 'dashMove 1s linear infinite';
        
        svg.appendChild(path);
        mapElement.appendChild(svg);
        
        this.currentPathSvg = svg;
    }
    
    animateMovement(startPos, endPos, destinationName) {
        const mapElement = document.getElementById('store-map');
        const gridContainer = document.getElementById('store-grid');
        if (!mapElement || !gridContainer) return;
        
        // Find current location marker
        const currentMarker = mapElement.querySelector('.map-marker.current-location');
        if (!currentMarker) return;
        
        // Calculate pixel positions
        const gridOffsetLeft = gridContainer.offsetLeft;
        const gridOffsetTop = gridContainer.offsetTop;
        
        const endX = gridOffsetLeft + (endPos.x / 100) * gridContainer.offsetWidth;
        const endY = gridOffsetTop + (endPos.y / 60) * gridContainer.offsetHeight;
        
        // Add moving class for smooth transition
        currentMarker.classList.add('moving');
        
        // Calculate animation duration based on distance
        const startX = parseFloat(currentMarker.style.left) || gridOffsetLeft;
        const startY = parseFloat(currentMarker.style.top) || gridOffsetTop;
        const distance = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
        const duration = Math.min(Math.max(distance * 5, 1000), 3000); // 1-3 seconds
        
        // Animate to destination
        setTimeout(() => {
            currentMarker.style.transition = `left ${duration}ms ease-in-out, top ${duration}ms ease-in-out`;
            currentMarker.style.left = endX + 'px';
            currentMarker.style.top = endY + 'px';
            
            // Update label
            const label = currentMarker.querySelector('.current-location-label');
            if (label) {
                label.textContent = 'You are here';
            }
        }, 100);
        
        // After animation completes
        setTimeout(() => {
            currentMarker.classList.remove('moving');
            this.lastDestination = destinationName;
            this.currentLocationName = destinationName;
            
            // Update location display
            this.updateLocationDisplay(destinationName);
            
            // Remove destination marker (we're there now)
            const destMarker = mapElement.querySelector('.map-marker.destination');
            if (destMarker) {
                destMarker.style.transition = 'opacity 0.5s';
                destMarker.style.opacity = '0';
                setTimeout(() => destMarker.remove(), 500);
            }
            
            // Clear navigation path
            setTimeout(() => {
                if (this.currentPathSvg) {
                    this.currentPathSvg.style.transition = 'opacity 0.5s';
                    this.currentPathSvg.style.opacity = '0';
                    setTimeout(() => {
                        if (this.currentPathSvg) {
                            this.currentPathSvg.remove();
                            this.currentPathSvg = null;
                        }
                    }, 500);
                }
            }, 500);
            
            this.showToast(`✅ Arrived at ${destinationName}`, 'success');
        }, duration + 200);
    }
    
    clearNavigationPath() {
        const mapElement = document.getElementById('store-map');
        if (!mapElement) return;
        
        // Remove SVG path
        mapElement.querySelectorAll('.navigation-path').forEach(el => el.remove());
        this.currentPathSvg = null;
        
        // Remove destination markers
        const destMarkers = mapElement.querySelectorAll('.map-marker.destination');
        destMarkers.forEach(marker => marker.remove());
        
        // Remove active navigation class
        mapElement.classList.remove('active-navigation');
        
        // Hide stop button
        const stopBtn = document.getElementById('stop-navigation');
        if (stopBtn) {
            stopBtn.style.display = 'none';
        }
        
        this.currentPath = null;
    }
    
    setupStopButton() {
        const stopBtn = document.getElementById('stop-navigation');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => {
                this.clearNavigationPath();
                this.showToast('Navigation stopped', 'info');
            });
        }
        
        const resetBtn = document.getElementById('reset-navigation');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetNavigation();
            });
        }
    }
    
    resetNavigation() {
        // Clear navigation path
        this.clearNavigationPath();
        
        // Reset last destination
        this.lastDestination = null;
        
        // Reset location display to entrance
        const locationElement = document.getElementById('current-location');
        if (locationElement) {
            locationElement.innerHTML = `📍 Entrance`;
        }
        
        // Re-render entire map at original position
        if (this.mapData) {
            this.currentLocationName = 'Entrance';
            this.currentLocationData = this.mapData.landmarks['Entrance'] || { x: 5, y: 5, name: 'Entrance' };
            
            // Re-render the map
            this.renderStoreMap(this.mapData);
        }
        
        // Hide reset button
        const resetBtn = document.getElementById('reset-navigation');
        if (resetBtn) {
            resetBtn.style.display = 'none';
        }
        
        // Hide stop button
        const stopBtn = document.getElementById('stop-navigation');
        if (stopBtn) {
            stopBtn.style.display = 'none';
        }
        
        this.showToast('🏠 Navigation reset to Entrance', 'success');
    }

    populateDestinations(landmarks, aisles) {
        const selects = [
            document.getElementById('destination-select'),
            document.getElementById('from-location'),
            document.getElementById('to-location'),
            document.getElementById('current-location-select')
        ];
        
        const allLocations = [...Object.keys(landmarks), ...Object.keys(aisles)];
        
        selects.forEach((select, index) => {
            if (!select) return;
            
            // Clear existing options
            const placeholders = [
                'Select a destination...',
                'Select starting location...',
                'Select destination...',
                'Where are you now?'
            ];
            
            select.innerHTML = `<option value="">${placeholders[index] || 'Select location...'}</option>`;
            
            // Add all locations
            allLocations.forEach(name => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                select.appendChild(option);
            });
        });
    }

    updateLocationDisplay(location) {
        const locationElement = document.getElementById('current-location');
        if (locationElement) {
            locationElement.textContent = `📍 ${location}`;
        }
        
        // Store current location info for map rendering
        this.currentLocationName = location.split(':')[0].trim();
        
        // Update map markers if map data is loaded
        if (this.mapData) {
            const gridSize = { cols: 12, rows: 10 };
            this.renderMapMarkers(this.mapData, gridSize);
        }
    }

    updateVoiceUI() {
        const voiceBtn = document.getElementById('voice-btn');
        const stopVoiceBtn = document.getElementById('stop-voice-btn');
        const listeningIndicator = document.getElementById('listening-indicator');
        
        if (voiceBtn) {
            if (this.isListening) {
                voiceBtn.classList.add('listening');
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i><span>Listening...</span>';
                voiceBtn.style.display = 'flex';
            } else {
                voiceBtn.classList.remove('listening');
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i><span>Press to Speak</span>';
                voiceBtn.style.display = 'flex';
            }
        }
        
        // Show/hide stop button based on listening state
        if (stopVoiceBtn) {
            stopVoiceBtn.style.display = this.isListening ? 'flex' : 'none';
        }
        
        if (listeningIndicator) {
            listeningIndicator.textContent = this.isListening ? '🔴 Listening...' : '🎤 Ready to listen';
        }
    }

    updateStatus(message) {
        const statusElement = document.getElementById('listening-indicator');
        if (statusElement) {
            statusElement.textContent = message;
        }
        
        // Auto-clear status after 3 seconds
        setTimeout(() => {
            if (statusElement && statusElement.textContent === message) {
                statusElement.textContent = this.isListening ? '🔴 Listening...' : '🎤 Ready to listen';
            }
        }, 3000);
    }

    speak(text) {
        if (!text) return;
        
        // Stop any ongoing speech
        this.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = this.settings.voiceSpeed;
        utterance.volume = this.settings.voiceVolume;
        
        // Show stop button when speaking starts
        utterance.onstart = () => {
            const stopBtn = document.getElementById('stop-speaking');
            if (stopBtn) {
                stopBtn.style.display = 'inline-flex';
            }
        };
        
        // Hide stop button when speaking ends
        utterance.onend = () => {
            const stopBtn = document.getElementById('stop-speaking');
            if (stopBtn) {
                stopBtn.style.display = 'none';
            }
        };
        
        // Handle errors
        utterance.onerror = () => {
            const stopBtn = document.getElementById('stop-speaking');
            if (stopBtn) {
                stopBtn.style.display = 'none';
            }
        };
        
        this.speechSynthesis.speak(utterance);
    }
    
    stopSpeaking() {
        // Cancel all speech synthesis
        this.speechSynthesis.cancel();
        
        // Hide stop button
        const stopBtn = document.getElementById('stop-speaking');
        if (stopBtn) {
            stopBtn.style.display = 'none';
        }
        
        this.showToast('Voice stopped', 'info');
    }
    
    speakCurrentResponse() {
        if (this.currentResponse) {
            this.speak(this.currentResponse);
        }
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.classList.toggle('active', show);
            loading.setAttribute('aria-hidden', !show);
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Show toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Remove toast after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                container.removeChild(toast);
            }, 300);
        }, 5000);
    }

    openSettings() {
        const modal = document.getElementById('settings-modal');
        if (modal) {
            // Populate current settings
            document.getElementById('voice-speed').value = this.settings.voiceSpeed;
            document.getElementById('voice-volume').value = this.settings.voiceVolume;
            document.getElementById('auto-speak').checked = this.settings.autoSpeak;
            document.getElementById('high-contrast').checked = this.settings.highContrast;
            
            this.updateSettingsDisplay();
            
            modal.classList.add('active');
            modal.setAttribute('aria-hidden', false);
        }
    }

    closeModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
            modal.setAttribute('aria-hidden', true);
        });
    }

    saveSettings() {
        // Get settings from form
        this.settings.voiceSpeed = parseFloat(document.getElementById('voice-speed').value);
        this.settings.voiceVolume = parseFloat(document.getElementById('voice-volume').value);
        this.settings.autoSpeak = document.getElementById('auto-speak').checked;
        this.settings.highContrast = document.getElementById('high-contrast').checked;
        
        // Save to localStorage
        localStorage.setItem('voiceNavigatorSettings', JSON.stringify(this.settings));
        
        // Apply settings
        this.applySettings();
        
        this.closeModal();
        this.showToast('Settings saved successfully', 'success');
    }

    loadSettings() {
        const saved = localStorage.getItem('voiceNavigatorSettings');
        if (saved) {
            try {
                this.settings = { ...this.settings, ...JSON.parse(saved) };
            } catch (error) {
                console.error('Error loading settings:', error);
            }
        }
    }

    applySettings() {
        // Apply high contrast mode
        document.body.classList.toggle('high-contrast', this.settings.highContrast);
        
        // Update settings display if modal is open
        this.updateSettingsDisplay();
    }

    updateSettingsDisplay() {
        const speedValue = document.getElementById('speed-value');
        const volumeValue = document.getElementById('volume-value');
        
        if (speedValue) {
            speedValue.textContent = this.settings.voiceSpeed.toFixed(1) + 'x';
        }
        
        if (volumeValue) {
            volumeValue.textContent = Math.round(this.settings.voiceVolume * 100) + '%';
        }
        
        // Add event listeners for real-time updates
        const speedSlider = document.getElementById('voice-speed');
        const volumeSlider = document.getElementById('voice-volume');
        
        if (speedSlider) {
            speedSlider.addEventListener('input', (e) => {
                if (speedValue) {
                    speedValue.textContent = parseFloat(e.target.value).toFixed(1) + 'x';
                }
            });
        }
        
        if (volumeSlider) {
            volumeSlider.addEventListener('input', (e) => {
                if (volumeValue) {
                    volumeValue.textContent = Math.round(parseFloat(e.target.value) * 100) + '%';
                }
            });
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.error('Error entering fullscreen:', err);
                this.showToast('Fullscreen not supported', 'warning');
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }
    
    showLocationUpdateNotification(newLocation) {
        // Extract the location name from the full description
        const locationName = newLocation.split(':')[0];
        this.showToast(`📍 Location updated to ${locationName}`, 'success');
    }
    
    async handleAdvancedDirections() {
        const fromSelect = document.getElementById('from-location');
        const toSelect = document.getElementById('to-location');
        
        const fromLocation = fromSelect.value;
        const toLocation = toSelect.value;
        
        if (!fromLocation || !toLocation) {
            this.showToast('Please select both starting and destination locations', 'warning');
            return;
        }
        
        if (fromLocation === toLocation) {
            this.showToast('Starting and destination locations cannot be the same', 'warning');
            return;
        }
        
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/directions_between', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    from: fromLocation,
                    to: toLocation
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.displayDirections(data.directions);
            
            // Show navigation path on map
            this.showNavigationPath(fromLocation, toLocation);
            
            if (this.settings.autoSpeak) {
                this.speak(data.directions);
            }
            
            this.showToast('Route calculated successfully', 'success');
            
        } catch (error) {
            console.error('Error getting advanced directions:', error);
            this.showToast('Error calculating route: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async handleUpdateLocation() {
        const locationSelect = document.getElementById('current-location-select');
        const selectedLocation = locationSelect.value;
        
        if (!selectedLocation) {
            this.showToast('Please select your current location', 'warning');
            return;
        }
        
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/set_location', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    location: selectedLocation
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.updateLocationDisplay(data.current_location);
            this.showToast(`Location updated to ${selectedLocation}`, 'success');
            
            // Reset the select
            locationSelect.value = '';
            
        } catch (error) {
            console.error('Error updating location:', error);
            this.showToast('Error updating location: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.voiceNavigator = new VoiceNavigatorApp();
});