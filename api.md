# API Documentation

## Supermarket Voice Navigator API

This document describes the internal API structure of the Supermarket Voice Navigator application.

## Core Modules

### VoiceInterface

Handles speech recognition and text-to-speech functionality.

#### Methods

- `listen(timeout=5, phrase_timeout=2)` - Listen for voice input
- `speak(text, interrupt_previous=True)` - Speak text using TTS
- `listen_with_confirmation(prompt, max_retries=3)` - Listen with confirmation
- `test_audio()` - Test audio system functionality

#### Configuration

Configured via Settings class with parameters:
- `speech_rate`: Words per minute (50-300)
- `speech_volume`: Volume level (0.0-1.0)
- `speech_language`: Recognition language code

### NavigationEngine

Handles pathfinding and location tracking within the supermarket.

#### Methods

- `get_current_location()` - Get current location description
- `set_current_location(location_name)` - Set current location
- `get_directions(destination)` - Get directions to destination
- `get_nearby_landmarks(radius=20)` - Get nearby landmarks
- `get_aisle_for_product(product)` - Find aisle containing product

#### Data Structures

- `Location(x, y, name, description)` - Represents a store location
- Store layout loaded from JSON configuration

### ProductLocator

Manages product search and location within the supermarket.

#### Methods

- `search_products(query)` - Search for products by query
- `get_product_guidance(product)` - Generate voice guidance for product
- `get_products_by_category(category)` - Get products in category
- `suggest_alternatives(product_name)` - Suggest alternative products

#### Data Structures

- `Product(name, category, aisle, location, description)` - Represents a product
- Product database with search capabilities and aliases

### Settings

Manages application configuration and settings.

#### Methods

- `get(key, default=None)` - Get setting value
- `set(key, value)` - Set setting value
- `load_config(config_file)` - Load from YAML file
- `save_config(config_file)` - Save to YAML file
- `validate_settings()` - Validate current settings

## Voice Commands

### Navigation Commands

- "go to [location]" - Navigate to specified location
- "where am I" - Get current location
- "directions to [location]" - Get detailed directions

### Product Search Commands

- "find [product]" - Search for specific product
- "where is [product]" - Locate product in store
- "looking for [product]" - Alternative search syntax

### Help Commands

- "help" - Get list of available commands
- "what can you do" - Get capability overview

### Exit Commands

- "exit", "quit", "goodbye", "stop" - End application

## Configuration Files

### config.yaml

Main configuration file containing:
- Voice interface settings
- Navigation parameters
- Product search configuration
- Accessibility options
- Performance settings

### Store Layout (JSON)

Store layout data structure:
```json
{
  "landmarks": [
    {
      "name": "Entrance",
      "x": 0,
      "y": 0,
      "description": "Main entrance"
    }
  ],
  "aisles": [
    {
      "name": "Aisle 1",
      "path": [
        {"x": 10, "y": 15},
        {"x": 10, "y": 45}
      ],
      "products": ["Bread", "Cereal", "Pasta"]
    }
  ]
}
```

### Products Database (JSON)

Product database structure:
```json
{
  "products": [
    {
      "name": "Bread",
      "category": "Bakery",
      "aisle": "Aisle 1",
      "description": "Fresh baked bread",
      "aliases": ["loaf", "white bread", "wheat bread"]
    }
  ]
}
```

## Error Handling

### Voice Recognition Errors

- `sr.UnknownValueError` - Could not understand audio
- `sr.RequestError` - Error with recognition service
- `sr.WaitTimeoutError` - No speech detected within timeout

### Navigation Errors

- Location not found - Returns available locations
- Invalid destination - Suggests similar locations
- Path calculation failure - Falls back to simple directions

### Product Search Errors

- Product not found - Suggests alternatives
- Multiple matches - Returns best match with confidence score
- Database loading failure - Uses default product set

## Logging

Log levels available:
- `DEBUG` - Detailed debugging information
- `INFO` - General information messages
- `WARNING` - Warning messages
- `ERROR` - Error messages

Log output includes:
- Timestamp
- Module name
- Log level
- Message content

## Environment Variables

- `OPENAI_API_KEY` - OpenAI API key for AI features
- `ANTHROPIC_API_KEY` - Anthropic API key for AI features
- `NAVIGATOR_SPEECH_RATE` - Override speech rate
- `NAVIGATOR_SPEECH_VOLUME` - Override speech volume
- `NAVIGATOR_DEBUG` - Enable debug mode