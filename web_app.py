#!/usr/bin/env python3
"""
Web Frontend for Supermarket Voice Navigator
Flask-based web interface for the voice navigation system.
"""

import logging
import json
import threading
import time
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import uuid

# Import existing modules
from voice_interface import VoiceInterface
from navigation import NavigationEngine
from product_locator import ProductLocator
from config.settings import Settings

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.secret_key = 'supermarket-navigator-secret-key'
CORS(app)

# Global instances
settings = Settings()
voice_interface = VoiceInterface(settings)
navigation_engine = NavigationEngine(settings)
product_locator = ProductLocator(settings)

# Active sessions for managing multiple users
active_sessions = {}

class WebSession:
    """Manages a web session for voice navigation."""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.current_location = "Entrance"
        self.is_listening = False
        self.last_command = ""
        self.last_response = ""
        self.created_at = time.time()

@app.route('/')
def index():
    """Main page of the web interface."""
    # Create or get session
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        active_sessions[session['session_id']] = WebSession(session['session_id'])
    
    return render_template('index.html')

@app.route('/api/process_command', methods=['POST'])
def process_command():
    """Process a voice command through the web interface."""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        session_id = session.get('session_id')
        if session_id not in active_sessions:
            active_sessions[session_id] = WebSession(session_id)
        
        web_session = active_sessions[session_id]
        web_session.last_command = command
        
        # Process the command using existing logic
        response = process_voice_command(command)
        web_session.last_response = response
        
        logger.info(f"Processed command: '{command}' -> '{response}'")
        
        # Extract destination information for map navigation
        destination_info = None
        command_lower = command.lower()
        
        # Check if this is a product search/navigation command
        if any(phrase in command_lower for phrase in ['find', 'locate', 'where is', 'take me', 'go to', 'navigate']):
            # Try to extract destination from the products
            products = product_locator.search_products(command)
            if products and products[0].aisle:
                aisle_name = products[0].aisle
                # Get the location coordinates
                location = None
                if aisle_name in navigation_engine.landmarks:
                    location = navigation_engine.landmarks[aisle_name]
                elif aisle_name in navigation_engine.aisles:
                    location = navigation_engine.aisles[aisle_name]['path'][0]
                
                if location:
                    destination_info = {
                        'name': aisle_name,
                        'x': location.x,
                        'y': location.y
                    }
        
        result = {
            'success': True,
            'command': command,
            'response': response,
            'current_location': navigation_engine.get_current_location(),
            'timestamp': time.time()
        }
        
        if destination_info:
            result['destination'] = destination_info
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_store_map')
def get_store_map():
    """Get the store layout for visualization."""
    try:
        store_data = {
            'landmarks': {},
            'aisles': {},
            'current_location': {
                'x': navigation_engine.current_location.x,
                'y': navigation_engine.current_location.y,
                'name': navigation_engine.current_location.name
            }
        }
        
        # Get landmarks
        for name, location in navigation_engine.landmarks.items():
            store_data['landmarks'][name] = {
                'x': location.x,
                'y': location.y,
                'name': location.name,
                'description': getattr(location, 'description', '')
            }
        
        # Get aisles
        for aisle_name, aisle_data in navigation_engine.aisles.items():
            store_data['aisles'][aisle_name] = {
                'path': [{'x': loc.x, 'y': loc.y} for loc in aisle_data['path']],
                'products': aisle_data.get('products', [])
            }
        
        return jsonify(store_data)
        
    except Exception as e:
        logger.error(f"Error getting store map: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_products')
def get_products():
    """Get all available products."""
    try:
        products_data = {
            'categories': product_locator.get_all_categories(),
            'products': {}
        }
        
        for product_name, product in product_locator.products.items():
            products_data['products'][product_name] = {
                'name': product.name,
                'category': product.category,
                'aisle': product.aisle,
                'description': getattr(product, 'description', ''),
                'aliases': getattr(product, 'aliases', [])
            }
        
        return jsonify(products_data)
        
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_products')
def search_products():
    """Search for products."""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        
        results = product_locator.search_products(query)
        
        search_results = []
        for product in results[:10]:  # Limit to top 10 results
            search_results.append({
                'name': product.name,
                'category': product.category,
                'aisle': product.aisle,
                'description': getattr(product, 'description', ''),
                'guidance': product_locator.get_product_guidance(product)
            })
        
        return jsonify({
            'query': query,
            'results': search_results,
            'count': len(search_results)
        })
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_directions')
def get_directions():
    """Get directions to a destination."""
    try:
        destination = request.args.get('destination', '')
        if not destination:
            return jsonify({'error': 'No destination provided'}), 400
        
        directions = navigation_engine.get_directions(destination)
        
        return jsonify({
            'destination': destination,
            'directions': directions,
            'current_location': navigation_engine.get_current_location()
        })
        
    except Exception as e:
        logger.error(f"Error getting directions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/set_location', methods=['POST'])
def set_location():
    """Set the current location."""
    try:
        data = request.get_json()
        location_name = data.get('location', '').strip()
        
        if not location_name:
            return jsonify({'error': 'No location provided'}), 400
        
        success = navigation_engine.set_current_location(location_name)
        
        return jsonify({
            'success': success,
            'current_location': navigation_engine.get_current_location(),
            'message': f'Location set to {location_name}' if success else f'Location {location_name} not found'
        })
        
    except Exception as e:
        logger.error(f"Error setting location: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/directions_between', methods=['POST'])
def get_directions_between():
    """Get directions between two specific locations."""
    try:
        data = request.get_json()
        from_location = data.get('from', '').strip()
        to_location = data.get('to', '').strip()
        
        if not from_location or not to_location:
            return jsonify({'error': 'Both from and to locations are required'}), 400
        
        directions = navigation_engine.get_directions_between_locations(from_location, to_location)
        
        return jsonify({
            'success': True,
            'from_location': from_location,
            'to_location': to_location,
            'directions': directions
        })
        
    except Exception as e:
        logger.error(f"Error getting directions between locations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/speak', methods=['POST'])
def speak_text():
    """Speak text using the TTS system."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Use existing voice interface
        voice_interface.speak(text)
        
        return jsonify({
            'success': True,
            'text': text,
            'message': 'Text spoken successfully'
        })
        
    except Exception as e:
        logger.error(f"Error speaking text: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session_info')
def session_info():
    """Get current session information."""
    try:
        session_id = session.get('session_id')
        if session_id not in active_sessions:
            return jsonify({'error': 'No active session'}), 404
        
        web_session = active_sessions[session_id]
        
        return jsonify({
            'session_id': session_id,
            'current_location': navigation_engine.get_current_location(),
            'last_command': web_session.last_command,
            'last_response': web_session.last_response,
            'created_at': web_session.created_at
        })
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        return jsonify({'error': str(e)}), 500

def process_voice_command(command: str) -> str:
    """Process a voice command using existing logic."""
    command_lower = command.lower()
    
    logger.info(f"Processing command: {command}")
    
    # Help command
    if 'help' in command_lower:
        return get_help_message()
    
    # Product search commands
    elif any(phrase in command_lower for phrase in ['find', 'where is', 'locate', 'looking for']):
        return handle_product_search(command)
    
    # Navigation commands
    elif any(phrase in command_lower for phrase in ['go to', 'navigate to', 'directions to', 'get directions']):
        return handle_navigation(command)
    
    # Status commands
    elif any(phrase in command_lower for phrase in ['where am i', 'current location', 'my location']):
        return navigation_engine.get_current_location()
    
    else:
        return "I didn't understand that command. Try 'help' for available options, or use the buttons below."

def get_help_message() -> str:
    """Return help message with available commands."""
    return (
        "Available commands: "
        "Say 'find' followed by a product name to locate items. "
        "Say 'go to' or 'get directions to' followed by a location for navigation. "
        "Say 'where am I' to get your current location. "
        "You can also use the buttons and controls on this page."
    )

def handle_product_search(command: str) -> str:
    """Handle product search commands and update current location."""
    try:
        products = product_locator.search_products(command)
        if products:
            product = products[0]
            
            # Store current location BEFORE updating
            old_location = navigation_engine.current_location.name
            old_location_description = navigation_engine.get_current_location()
            
            # Generate guidance
            guidance = f"I found {product.name}! "
            
            if product.aisle:
                guidance += f"You can find it in {product.aisle}. "
                
                # Get directions from OLD location to NEW location
                if old_location != product.aisle:
                    try:
                        directions = navigation_engine.get_directions_between_locations(old_location, product.aisle)
                        guidance += f"\n\n{directions}"
                    except Exception as nav_error:
                        logger.debug(f"Could not get navigation directions: {nav_error}")
                        guidance += f"Head from {old_location} to {product.aisle} to find it."
                else:
                    guidance += "You're already in the right section! Look around for the product."
                
                # NOW update location to new product location
                success = navigation_engine.set_current_location(product.aisle)
                if success:
                    logger.info(f"Updated location from {old_location} to {product.aisle} after finding {product.name}")
                    guidance += f"\n\nI've updated your location to {product.aisle}."
            
            if product.category:
                guidance += f" It's in the {product.category} section."
            
            return guidance
        else:
            return "I couldn't find that product. Could you try rephrasing or ask for a similar item?"
    except Exception as e:
        logger.error(f"Error in product search: {e}")
        return "I'm having trouble searching for that product right now."

def handle_navigation(command: str) -> str:
    """Handle navigation commands."""
    try:
        directions = navigation_engine.get_directions(command)
        return directions
    except Exception as e:
        logger.error(f"Error in navigation: {e}")
        return "I'm having trouble with navigation right now."

if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Supermarket Voice Navigator Web Interface")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)