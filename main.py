#!/usr/bin/env python3
"""
Supermarket Voice Navigator - Main Application
An AI-powered assistant for visually impaired people to navigate supermarkets.
"""

import logging
import sys
from pathlib import Path
import click

# Add the src directory to the path for imports
sys.path.append(str(Path(__file__).parent))

from voice_interface import VoiceInterface
from navigation import NavigationEngine
from product_locator import ProductLocator
from config.settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SupermarketAssistant:
    """Main application class for the supermarket voice navigator."""
    
    def __init__(self):
        """Initialize the supermarket assistant."""
        logger.info("Initializing Supermarket Voice Navigator...")
        
        self.settings = Settings()
        self.voice_interface = VoiceInterface(self.settings)
        self.navigation_engine = NavigationEngine(self.settings)
        self.product_locator = ProductLocator(self.settings)
        
        logger.info("Assistant initialized successfully!")
    
    def start(self):
        """Start the main application loop."""
        logger.info("Starting Supermarket Voice Navigator...")
        
        # Welcome message
        self.voice_interface.speak(
            "Welcome to the Supermarket Voice Navigator! "
            "I'm here to help you navigate the store and find products. "
            "You can ask me to find items, get directions, or say 'help' for more options."
        )
        
        try:
            while True:
                # Listen for user command
                command = self.voice_interface.listen()
                
                if command:
                    response = self.process_command(command)
                    if response:
                        self.voice_interface.speak(response)
                    
                    # Check for exit commands
                    if any(word in command.lower() for word in ['exit', 'quit', 'goodbye', 'stop']):
                        self.voice_interface.speak("Thank you for using Supermarket Voice Navigator. Have a great shopping trip!")
                        break
                        
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
            self.voice_interface.speak("Goodbye!")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.voice_interface.speak("I'm sorry, there was an unexpected error. Please restart the application.")
    
    def process_command(self, command: str) -> str:
        """Process a voice command and return appropriate response."""
        command_lower = command.lower()
        
        logger.info(f"Processing command: {command}")
        
        # Help command
        if 'help' in command_lower:
            return self._get_help_message()
        
        # Product search commands
        elif any(phrase in command_lower for phrase in ['find', 'where is', 'locate', 'looking for']):
            return self._handle_product_search(command)
        
        # Navigation commands
        elif any(phrase in command_lower for phrase in ['go to', 'navigate to', 'directions to', 'get directions']):
            return self._handle_navigation(command)
        
        # Status commands
        elif any(phrase in command_lower for phrase in ['where am i', 'current location', 'my location']):
            return self._handle_location_status()
        
        else:
            return "I didn't understand that command. Say 'help' for available options."
    
    def _get_help_message(self) -> str:
        """Return help message with available commands."""
        return (
            "Here are the available commands: "
            "Say 'find' followed by a product name to locate items. "
            "Say 'go to' or 'get directions to' followed by a location for navigation. "
            "Say 'where am I' to get your current location. "
            "Say 'exit' or 'quit' to stop the assistant."
        )
    
    def _handle_product_search(self, command: str) -> str:
        """Handle product search commands and update current location."""
        try:
            products = self.product_locator.search_products(command)
            if products:
                product = products[0]
                
                # Store current location BEFORE updating
                old_location = self.navigation_engine.current_location.name
                
                # Generate guidance
                guidance = f"I found {product.name}! "
                
                if product.aisle:
                    guidance += f"You can find it in {product.aisle}. "
                    
                    # Get directions from OLD location to NEW location
                    if old_location != product.aisle:
                        try:
                            directions = self.navigation_engine.get_directions_between_locations(old_location, product.aisle)
                            guidance += f"\n\n{directions}"
                        except Exception as nav_error:
                            logger.debug(f"Could not get navigation directions: {nav_error}")
                            guidance += f"Head from {old_location} to {product.aisle} to find it."
                    else:
                        guidance += "You're already in the right section! Look around for the product."
                    
                    # NOW update location to new product location
                    success = self.navigation_engine.set_current_location(product.aisle)
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
    
    def _handle_navigation(self, command: str) -> str:
        """Handle navigation commands."""
        try:
            directions = self.navigation_engine.get_directions(command)
            return directions
        except Exception as e:
            logger.error(f"Error in navigation: {e}")
            return "I'm having trouble with navigation right now."
    
    def _handle_location_status(self) -> str:
        """Handle location status requests."""
        try:
            location = self.navigation_engine.get_current_location()
            return f"You are currently at {location}"
        except Exception as e:
            logger.error(f"Error getting location: {e}")
            return "I'm not sure where you are right now."


@click.command()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--config', type=click.Path(exists=True), help='Path to configuration file')
def main(debug, config):
    """Main entry point for the Supermarket Voice Navigator."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    if config:
        logger.info(f"Using configuration file: {config}")
        # TODO: Load custom configuration
    
    try:
        assistant = SupermarketAssistant()
        assistant.start()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()