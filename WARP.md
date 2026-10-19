# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Python-based AI-powered voice navigation assistant designed for visually impaired users in supermarket environments. The application uses speech recognition, text-to-speech, and AI models to provide real-time navigation guidance and product location assistance.

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

#### Terminal/Console Version
```bash
# Run main application
python src/main.py

# Run with debug mode
python src/main.py --debug

# Run with custom config
python src/main.py --config path/to/config.yaml

# Run directly from source
python -m src.main
```

#### Web Interface Version
```bash
# Run web application (recommended)
python src/web_app.py

# Or with gunicorn for production
gunicorn -w 4 -b 0.0.0.0:5000 src.web_app:app

# Access at http://localhost:5000
```

### Development & Testing
```bash
# Run linting
flake8 src/
black src/ --check

# Format code
black src/

# Type checking
mypy src/

# Run tests (when implemented)
pytest
pytest --cov=src tests/
```

### Audio Testing
```bash
# Test audio system directly
python -c "from src.voice_interface import VoiceInterface; from src.config.settings import Settings; vi = VoiceInterface(Settings()); vi.test_audio()"
```

## High-Level Architecture

### Core Component Structure
The application follows a modular architecture with four main components orchestrated by a central `SupermarketAssistant` class:

- **VoiceInterface**: Handles all speech recognition and text-to-speech operations
- **NavigationEngine**: Manages store layout, pathfinding, and location tracking
- **ProductLocator**: Handles product database and search functionality
- **Settings**: Centralized configuration management

### Web Interface Architecture
The web frontend extends the core architecture with:

- **Flask Web App** (`web_app.py`): RESTful API server with session management
- **HTML Templates** (`templates/`): Accessible web interface with ARIA labels
- **CSS Styling** (`static/styles.css`): Responsive design with accessibility features
- **JavaScript Frontend** (`static/app.js`): Client-side voice recognition and API communication
- **Browser APIs**: Web Speech API for voice recognition and synthesis

### Data Flow
1. Voice input → `VoiceInterface.listen()` → Speech recognition
2. Command processing → `SupermarketAssistant.process_command()` → Intent classification
3. Business logic → Appropriate module (`NavigationEngine`/`ProductLocator`)
4. Response generation → Text response
5. Voice output → `VoiceInterface.speak()` → Text-to-speech

### Configuration Architecture
The application uses a layered configuration system:
1. **Default values** in `Settings` class
2. **YAML configuration** from `config.yaml`
3. **Environment variables** (highest priority)

Key environment variables:
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`: AI service keys
- `NAVIGATOR_*`: Override configuration values
- `NAVIGATOR_DEBUG`: Enable debug logging

### Location and Product Data
- **Store layouts**: JSON files in `data/store_layouts/` with coordinate-based mapping
- **Product database**: JSON files in `data/products.json` with category/aisle mapping
- **Dynamic loading**: Falls back to hardcoded defaults if files not found

### Voice Command Processing
The system uses keyword-based command routing:
- **Navigation**: "go to", "navigate to", "directions to" → `NavigationEngine`
- **Product search**: "find", "where is", "locate" → `ProductLocator`
- **Status**: "where am i", "current location" → Location queries
- **Help/Exit**: Built-in commands for assistance and termination

### Audio System Design
- **Threading**: TTS runs in separate threads to prevent blocking
- **Calibration**: Automatic ambient noise adjustment on startup
- **Timeout handling**: Configurable timeouts for speech detection
- **Error recovery**: Graceful degradation when audio services fail

## Key Development Patterns

### Error Handling Strategy
- All voice operations have fallback error messages
- Audio failures don't crash the application
- Missing data files trigger default data generation
- Logging at appropriate levels for debugging

### Extensibility Points
- **New voice commands**: Add patterns to `process_command()` method (both console and web versions)
- **New locations**: Extend store layout JSON files
- **New products**: Add to product database JSON
- **AI integration**: Already configured for OpenAI/Anthropic APIs
- **New web features**: Add API endpoints to `web_app.py` and corresponding frontend functionality
- **UI customization**: Modify CSS variables in `styles.css` for theming

### Configuration Management
- Settings use property decorators for type safety
- Environment variable override system for deployment
- Validation methods ensure configuration integrity
- YAML-based configuration for easy modification

## Voice Interface Integration

### Speech Recognition Flow
The system uses Google's speech recognition service with:
- Configurable timeouts and phrase limits
- Ambient noise calibration
- Confirmation workflows for critical operations
- Graceful timeout and error handling

### TTS Configuration
- Automatic voice selection (prefers female voices for accessibility)
- Configurable speech rate and volume
- Threading to prevent blocking user interactions
- Interrupt capability for responsive user experience

## Data Architecture

### Location System
- Coordinate-based positioning (x, y)
- Named landmarks and aisles
- Distance calculation and pathfinding
- Direction generation ("north", "south", etc.)

### Product Search
- Multi-field matching (name, aliases, category)
- Confidence scoring system
- Alternative product suggestions
- Category-based organization

### Configuration Hierarchy
1. Hardcoded defaults in `Settings.defaults`
2. YAML file configuration (`config.yaml`)
3. Environment variable overrides
4. Runtime modifications via `Settings.set()`

## Web Interface Features

### Accessibility Design
- **WCAG compliant**: ARIA labels, keyboard navigation, screen reader support
- **High contrast mode**: Toggle for visual accessibility
- **Voice controls**: Browser-based speech recognition and synthesis
- **Responsive design**: Works on desktop, tablet, and mobile devices
- **Settings persistence**: User preferences saved in localStorage

### Interactive Components
- **Voice button**: Large, accessible microphone button with visual feedback
- **Text input**: Alternative to voice commands for all functionality
- **Quick actions**: Pre-defined command buttons for common tasks
- **Product search**: Real-time search with clickable results
- **Store map visualization**: Visual representation of store layout
- **Navigation panel**: Destination selection and turn-by-turn directions
- **Settings modal**: Voice speed, volume, and accessibility options

### Browser Compatibility
- **Speech Recognition**: Chrome, Edge (full support), Firefox/Safari (limited)
- **Speech Synthesis**: All modern browsers
- **Responsive Design**: All modern browsers
- **Accessibility Features**: All browsers with screen reader support

## AI Integration Readiness

The codebase is prepared for AI enhancement with:
- API key management through environment variables
- Configurable AI models and response lengths
- Structured command processing suitable for AI routing
- Voice interface compatible with AI-generated responses
- Web API endpoints ready for AI service integration

<citations>
<document>
  <document_type>WARP_DOCUMENTATION</document_type>
  <document_id>getting-started/quickstart-guide/coding-in-warp</document_id>
</document>
</citations>