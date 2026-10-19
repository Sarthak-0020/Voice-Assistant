"""
Navigation Engine Module
Handles pathfinding, directions, and location tracking within the supermarket.
"""

import logging
import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import math

logger = logging.getLogger(__name__)


class Location:
    """Represents a location in the supermarket."""
    
    def __init__(self, x: float, y: float, name: str = "", description: str = ""):
        self.x = x
        self.y = y
        self.name = name
        self.description = description
    
    def distance_to(self, other: 'Location') -> float:
        """Calculate distance to another location."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __str__(self):
        return f"{self.name} at ({self.x}, {self.y})"


class NavigationEngine:
    """Handles navigation and pathfinding within the supermarket."""
    
    def __init__(self, settings):
        """Initialize the navigation engine."""
        self.settings = settings
        self.current_location = Location(0, 0, "Entrance", "Main entrance of the store")
        self.store_layout = {}
        self.landmarks = {}
        self.aisles = {}
        
        # Load store layout data
        self._load_store_layout()
        
        logger.info("Navigation engine initialized")
    
    def _load_store_layout(self):
        """Load store layout from configuration files."""
        try:
            # Try to load store layout from data directory
            layout_path = Path("data/store_layouts/default_layout.json")
            
            if layout_path.exists():
                with open(layout_path, 'r') as f:
                    layout_data = json.load(f)
                    self._parse_layout_data(layout_data)
            else:
                # Use default layout if no file found
                self._create_default_layout()
                
            logger.info(f"Store layout loaded: {len(self.landmarks)} landmarks, {len(self.aisles)} aisles")
            
        except Exception as e:
            logger.warning(f"Could not load store layout: {e}. Using default layout.")
            self._create_default_layout()
    
    def _parse_layout_data(self, layout_data: dict):
        """Parse layout data from JSON."""
        # Load landmarks
        for landmark_data in layout_data.get('landmarks', []):
            loc = Location(
                landmark_data['x'],
                landmark_data['y'],
                landmark_data['name'],
                landmark_data.get('description', '')
            )
            self.landmarks[landmark_data['name']] = loc
        
        # Load aisles
        for aisle_data in layout_data.get('aisles', []):
            aisle_locations = []
            for point in aisle_data['path']:
                aisle_locations.append(Location(point['x'], point['y']))
            
            self.aisles[aisle_data['name']] = {
                'path': aisle_locations,
                'products': aisle_data.get('products', [])
            }
    
    def _create_default_layout(self):
        """Create a comprehensive default store layout."""
        # Default landmarks - aligned with visual map coordinates (0-100 for x, 0-60 for y)
        self.landmarks = {
            'Entrance': Location(5, 3, 'Entrance', 'Main entrance'),
            'Customer Service': Location(10, 3, 'Customer Service', 'Customer service desk and returns'),
            'Pharmacy': Location(50, 6, 'Pharmacy', 'Pharmacy counter and health products'),
            'Deli': Location(35, 7.5, 'Deli', 'Deli counter - fresh meat and seafood'),
            'Bakery': Location(65, 7.5, 'Bakery', 'Fresh bakery - bread, cakes, and pastries'),
            'Produce': Location(87.5, 15, 'Produce', 'Fresh fruits and vegetables'),
            'Dairy': Location(87.5, 33, 'Dairy', 'Milk, cheese, yogurt, and dairy products'),
            'Household': Location(87.5, 48, 'Household', 'Cleaning supplies and household items'),
            'Baby Care': Location(22.5, 52.5, 'Baby Care', 'Baby products and infant care'),
            'Pet Care': Location(42.5, 52.5, 'Pet Care', 'Pet food and pet supplies'),
            'Checkout': Location(8, 42, 'Checkout', 'Checkout lanes and self-checkout'),
            'Exit': Location(5, 33, 'Exit', 'Store exit')
        }
        
        # Comprehensive aisles - exact centers matching visual map (0-100 for x, 0-60 for y)
        self.aisles = {
            'Aisle 1': {
                'path': [Location(19, 30), Location(19, 30)],
                'products': [
                    'Rice', 'Pasta', 'Quinoa', 'Flour', 'Sugar', 'Salt', 'Black Pepper',
                    'Olive Oil', 'Vegetable Oil', 'Vinegar', 'Cereal', 'Oatmeal',
                    'Pancake Mix', 'Syrup', 'Peanut Butter', 'Jelly'
                ]
            },
            'Aisle 2': {
                'path': [Location(32, 30), Location(32, 30)],
                'products': [
                    'Canned Tomatoes', 'Canned Beans', 'Soup', 'Canned Tuna', 'Chicken Broth',
                    'Coconut Milk', 'Corn', 'Green Beans'
                ]
            },
            'Aisle 3': {
                'path': [Location(45, 30), Location(45, 30)],
                'products': [
                    'Chips', 'Pretzels', 'Popcorn', 'Crackers', 'Nuts', 'Trail Mix',
                    'Granola Bars', 'Candy'
                ]
            },
            'Aisle 4': {
                'path': [Location(58, 30), Location(58, 30)],
                'products': [
                    'Water', 'Soda', 'Juice', 'Coffee', 'Tea', 'Energy Drinks',
                    'Beer', 'Wine'
                ]
            },
            'Aisle 5': {
                'path': [Location(71, 30), Location(71, 30)],
                'products': [
                    'Ice Cream', 'Frozen Pizza', 'Frozen Vegetables', 'Frozen Fruit',
                    'Frozen Meals', 'French Fries', 'Frozen Chicken', 'Frozen Waffles'
                ]
            },
            'Produce': {
                'path': [Location(87.5, 15), Location(87.5, 15)],
                'products': [
                    'Apples', 'Bananas', 'Oranges', 'Lemons', 'Limes', 'Grapes',
                    'Strawberries', 'Blueberries', 'Raspberries', 'Blackberries',
                    'Carrots', 'Lettuce', 'Spinach', 'Broccoli', 'Bell Peppers', 
                    'Onions', 'Tomatoes', 'Cucumbers', 'Potatoes'
                ]
            },
            'Dairy': {
                'path': [Location(87.5, 33), Location(87.5, 33)],
                'products': [
                    'Milk', 'Cheese', 'Yogurt', 'Butter', 'Eggs', 'Cream Cheese',
                    'Sour Cream', 'Heavy Cream'
                ]
            },
            'Deli': {
                'path': [Location(35, 7.5), Location(35, 7.5)],
                'products': [
                    'Chicken Breast', 'Ground Beef', 'Pork Chops', 'Bacon', 'Ham',
                    'Turkey', 'Salmon', 'Shrimp'
                ]
            },
            'Bakery': {
                'path': [Location(65, 7.5), Location(65, 7.5)],
                'products': [
                    'Bread', 'Bagels', 'Croissants', 'Muffins', 'Donuts', 'Cookies',
                    'Cake'
                ]
            },
            'Pharmacy': {
                'path': [Location(50, 6), Location(50, 6)],
                'products': [
                    'Shampoo', 'Conditioner', 'Toothpaste', 'Toothbrush', 'Soap',
                    'Deodorant', 'Vitamins', 'Pain Relief'
                ]
            },
            'Household': {
                'path': [Location(87.5, 48), Location(87.5, 48)],
                'products': [
                    'Toilet Paper', 'Paper Towels', 'Laundry Detergent', 'Dish Soap',
                    'Trash Bags', 'Aluminum Foil', 'Plastic Wrap'
                ]
            },
            'Baby Care': {
                'path': [Location(22.5, 52.5), Location(22.5, 52.5)],
                'products': [
                    'Diapers', 'Baby Food', 'Baby Wipes'
                ]
            },
            'Pet Care': {
                'path': [Location(42.5, 52.5), Location(42.5, 52.5)],
                'products': [
                    'Dog Food', 'Cat Food', 'Cat Litter', 'Dog Treats'
                ]
            }
        }
    
    def get_current_location(self) -> str:
        """Get the current location description."""
        return f"{self.current_location.name}: {self.current_location.description}"
    
    def set_current_location(self, location_name: str) -> bool:
        """Set the current location by name."""
        location_name_lower = location_name.lower()
        
        # First check exact match in landmarks
        if location_name in self.landmarks:
            self.current_location = self.landmarks[location_name]
            logger.info(f"Location set to landmark: {self.current_location}")
            return True
        
        # Check exact match in aisles
        if location_name in self.aisles:
            aisle_data = self.aisles[location_name]
            # Create a proper location object for the aisle
            aisle_start = aisle_data['path'][0]
            self.current_location = Location(
                aisle_start.x, 
                aisle_start.y, 
                location_name,
                f"{location_name} - {', '.join(aisle_data['products'][:3])}..."
            )
            logger.info(f"Location set to aisle: {self.current_location}")
            return True
        
        # Check partial matches in landmarks
        for landmark_name in self.landmarks:
            if location_name_lower in landmark_name.lower() or landmark_name.lower() in location_name_lower:
                self.current_location = self.landmarks[landmark_name]
                logger.info(f"Location set to landmark (partial match): {self.current_location}")
                return True
        
        # Check partial matches in aisles
        for aisle_name, aisle_data in self.aisles.items():
            if location_name_lower in aisle_name.lower() or aisle_name.lower() in location_name_lower:
                aisle_start = aisle_data['path'][0]
                self.current_location = Location(
                    aisle_start.x, 
                    aisle_start.y, 
                    aisle_name,
                    f"{aisle_name} - {', '.join(aisle_data['products'][:3])}..."
                )
                logger.info(f"Location set to aisle (partial match): {self.current_location}")
                return True
        
        logger.warning(f"Location '{location_name}' not found")
        return False
    
    def find_nearest_landmark(self, location: Location) -> Tuple[str, Location]:
        """Find the nearest landmark to a given location."""
        if not self.landmarks:
            return "Unknown", location
        
        nearest_name = min(self.landmarks.keys(), 
                         key=lambda name: location.distance_to(self.landmarks[name]))
        return nearest_name, self.landmarks[nearest_name]
    
    def get_directions(self, destination: str) -> str:
        """Get directions from current location to destination."""
        destination = destination.lower().strip()
        
        # Clean up the destination string (remove command words)
        for phrase in ['go to', 'navigate to', 'directions to', 'take me to']:
            if destination.startswith(phrase):
                destination = destination[len(phrase):].strip()
        
        target_location = self._find_destination(destination)
        
        if not target_location:
            available_locations = list(self.landmarks.keys()) + list(self.aisles.keys())
            return f"I couldn't find '{destination}'. Available locations include: {', '.join(available_locations[:10])} and more."
        
        # Generate comprehensive directions
        directions = self._generate_comprehensive_directions(self.current_location, target_location)
        
        return directions
    
    def get_directions_between_locations(self, from_location: str, to_location: str) -> str:
        """Get directions between two specific locations."""
        from_loc = self._find_destination(from_location.lower())
        to_loc = self._find_destination(to_location.lower())
        
        if not from_loc:
            return f"I couldn't find the starting location '{from_location}'."
        
        if not to_loc:
            return f"I couldn't find the destination '{to_location}'."
        
        directions = self._generate_comprehensive_directions(from_loc, to_loc)
        
        return directions
    
    def _find_destination(self, destination: str) -> Optional[Location]:
        """Find a destination location by name or partial match."""
        destination = destination.lower()
        
        # Exact match in landmarks
        for name, location in self.landmarks.items():
            if name.lower() == destination:
                return location
        
        # Partial match in landmarks
        for name, location in self.landmarks.items():
            if destination in name.lower() or name.lower() in destination:
                return location
        
        # Check aisles - create a proper copy to avoid modifying original
        for aisle_name, aisle_data in self.aisles.items():
            if destination in aisle_name.lower() or aisle_name.lower() in destination:
                # Create a copy of the location to avoid modifying the original
                aisle_start = aisle_data['path'][0]
                aisle_location = Location(
                    aisle_start.x, 
                    aisle_start.y, 
                    aisle_name, 
                    f"{aisle_name} - {', '.join(aisle_data['products'][:3])}..."
                )
                return aisle_location
        
        return None
    
    def _get_direction(self, from_loc: Location, to_loc: Location) -> str:
        """Get cardinal direction from one location to another."""
        dx = to_loc.x - from_loc.x
        dy = to_loc.y - from_loc.y
        
        if abs(dx) > abs(dy):
            return "east" if dx > 0 else "west"
        else:
            return "north" if dy > 0 else "south"
    
    def _generate_directions(self, from_loc: Location, to_loc: Location) -> str:
        """Generate human-readable directions."""
        distance = from_loc.distance_to(to_loc)
        direction = self._get_direction(from_loc, to_loc)
        
        # Convert distance to steps (assuming 1 unit = 2 steps)
        steps = int(distance * 2)
        
        if distance < 5:
            distance_desc = "very close by"
        elif distance < 15:
            distance_desc = "nearby"
        elif distance < 30:
            distance_desc = "a moderate walk"
        else:
            distance_desc = "across the store"
        
        directions = f"From {from_loc.name}, head {direction} to reach {to_loc.name}. "
        directions += f"It's {distance_desc}, approximately {steps} steps away. "
        
        # Add additional context if available
        if hasattr(to_loc, 'description') and to_loc.description:
            directions += f"Look for {to_loc.description}."
        
        return directions
    
    def _generate_comprehensive_directions(self, from_loc: Location, to_loc: Location) -> str:
        """Generate comprehensive step-by-step directions between two locations."""
        distance = from_loc.distance_to(to_loc)
        direction = self._get_direction(from_loc, to_loc)
        
        # Convert distance to steps (assuming 1 unit = 2 steps)
        steps = int(distance * 2)
        
        # Determine distance category
        if distance < 10:
            distance_desc = "very close"
            walk_time = "less than 1 minute"
        elif distance < 25:
            distance_desc = "nearby"
            walk_time = "about 1-2 minutes"
        elif distance < 50:
            distance_desc = "a moderate walk"
            walk_time = "about 2-3 minutes"
        else:
            distance_desc = "across the store"
            walk_time = "about 3-5 minutes"
        
        # Generate step-by-step directions
        directions = f"🎯 Navigation from {from_loc.name} to {to_loc.name}\n\n"
        
        # Step 1: Starting point
        directions += f"🏁 Starting Point: {from_loc.name}\n"
        if hasattr(from_loc, 'description') and from_loc.description:
            directions += f"   {from_loc.description}\n\n"
        
        # Step 2: Direction and distance
        directions += f"🧭 Direction: Head {direction}\n"
        directions += f"📏 Distance: {distance_desc} ({steps} steps, {walk_time})\n\n"
        
        # Step 3: Route guidance
        route_guidance = self._get_route_guidance(from_loc, to_loc, direction)
        directions += f"🛤️ Route: {route_guidance}\n\n"
        
        # Step 4: Destination details
        directions += f"🎯 Destination: {to_loc.name}\n"
        if hasattr(to_loc, 'description') and to_loc.description:
            directions += f"   {to_loc.description}\n\n"
        
        # Step 5: Landmarks to look for
        landmarks = self._get_landmarks_along_route(from_loc, to_loc)
        if landmarks:
            directions += f"👀 Look for: {landmarks}\n\n"
        
        # Step 6: Arrival confirmation
        directions += f"✅ You'll know you're there when: You see {to_loc.name}"
        
        return directions
    
    def _get_route_guidance(self, from_loc: Location, to_loc: Location, direction: str) -> str:
        """Get specific route guidance based on store layout."""
        # Calculate the path through the store
        dx = to_loc.x - from_loc.x
        dy = to_loc.y - from_loc.y
        
        guidance_parts = []
        
        # Horizontal movement
        if abs(dx) > 5:
            if dx > 0:
                guidance_parts.append("walk towards the back of the store")
            else:
                guidance_parts.append("walk towards the front of the store")
        
        # Vertical movement  
        if abs(dy) > 5:
            if dy > 0:
                guidance_parts.append("turn towards the right side of the store")
            else:
                guidance_parts.append("turn towards the left side of the store")
        
        if not guidance_parts:
            return "It's right nearby, just a few steps away"
        
        return ", then ".join(guidance_parts)
    
    def _get_landmarks_along_route(self, from_loc: Location, to_loc: Location) -> str:
        """Identify landmarks along the route for better navigation."""
        landmarks = []
        
        # Find intermediate landmarks
        mid_x = (from_loc.x + to_loc.x) / 2
        mid_y = (from_loc.y + to_loc.y) / 2
        
        # Check for landmarks near the route
        for name, location in self.landmarks.items():
            if name != from_loc.name and name != to_loc.name:
                # Check if landmark is reasonably close to the route
                dist_to_route = abs((location.x - mid_x) + (location.y - mid_y))
                if dist_to_route < 20:
                    landmarks.append(name)
        
        # Also check aisles along the route
        for aisle_name, aisle_data in self.aisles.items():
            if aisle_name != from_loc.name and aisle_name != to_loc.name:
                aisle_start = aisle_data['path'][0]
                dist_to_route = abs((aisle_start.x - mid_x) + (aisle_start.y - mid_y))
                if dist_to_route < 15:
                    landmarks.append(aisle_name)
        
        if landmarks:
            return f"You'll pass by {', '.join(landmarks[:3])}"
        return ""
    
    def get_nearby_landmarks(self, radius: float = 20) -> List[str]:
        """Get landmarks within a certain radius of current location."""
        nearby = []
        
        for name, location in self.landmarks.items():
            if self.current_location.distance_to(location) <= radius:
                nearby.append(name)
        
        return nearby
    
    def get_aisle_for_product(self, product: str) -> Optional[str]:
        """Find which aisle contains a specific product."""
        product_lower = product.lower()
        
        for aisle_name, aisle_data in self.aisles.items():
            for aisle_product in aisle_data.get('products', []):
                if product_lower in aisle_product.lower() or aisle_product.lower() in product_lower:
                    return aisle_name
        
        return None
