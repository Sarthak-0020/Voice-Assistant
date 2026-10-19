"""
Product Locator Module
Handles product search and location within the supermarket.
"""

import logging
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re
from navigation import NavigationEngine, Location

logger = logging.getLogger(__name__)


class Product:
    """Represents a product in the supermarket."""
    
    def __init__(self, name: str, category: str, aisle: str, location: Optional[Location] = None, description: str = ""):
        self.name = name
        self.category = category
        self.aisle = aisle
        self.location = location
        self.description = description
        self.aliases = []  # Alternative names for the product
    
    def add_alias(self, alias: str):
        """Add an alternative name for this product."""
        self.aliases.append(alias.lower())
    
    def matches_query(self, query: str) -> float:
        """Check if this product matches a search query and return confidence score."""
        query_lower = query.lower()
        
        # Exact match with name
        if query_lower == self.name.lower():
            return 1.0
        
        # Exact match with alias
        if query_lower in [alias.lower() for alias in self.aliases]:
            return 0.9
        
        # Partial match with name
        if query_lower in self.name.lower() or self.name.lower() in query_lower:
            return 0.8
        
        # Partial match with alias
        for alias in self.aliases:
            if query_lower in alias.lower() or alias.lower() in query_lower:
                return 0.7
        
        # Category match
        if query_lower in self.category.lower() or self.category.lower() in query_lower:
            return 0.5
        
        return 0.0


class ProductLocator:
    """Handles product search and location functionality."""
    
    def __init__(self, settings):
        """Initialize the product locator."""
        self.settings = settings
        self.products = {}  # Dict[str, Product]
        self.categories = {}  # Dict[str, List[Product]]
        
        # Load product database
        self._load_product_database()
        
        logger.info(f"Product locator initialized with {len(self.products)} products")
    
    def _load_product_database(self):
        """Load product database from configuration files."""
        try:
            # Try to load from data directory
            products_path = Path("data/products.json")
            
            if products_path.exists():
                with open(products_path, 'r') as f:
                    products_data = json.load(f)
                    self._parse_products_data(products_data)
            else:
                # Create default product database
                self._create_default_products()
                
            self._organize_by_categories()
            
        except Exception as e:
            logger.warning(f"Could not load product database: {e}. Using defaults.")
            self._create_default_products()
            self._organize_by_categories()
    
    def _parse_products_data(self, products_data: dict):
        """Parse products data from JSON."""
        for product_data in products_data.get('products', []):
            product = Product(
                name=product_data['name'],
                category=product_data['category'],
                aisle=product_data['aisle'],
                description=product_data.get('description', '')
            )
            
            # Add aliases
            for alias in product_data.get('aliases', []):
                product.add_alias(alias)
            
            self.products[product.name] = product
    
    def _create_default_products(self):
        """Create a comprehensive default product database."""
        default_products = [
            # PRODUCE SECTION
            # Fruits
            {"name": "Apples", "category": "Produce", "aisle": "Produce", "aliases": ["red apples", "green apples", "granny smith", "gala", "fuji"]},
            {"name": "Bananas", "category": "Produce", "aisle": "Produce", "aliases": ["yellow bananas", "ripe bananas"]},
            {"name": "Oranges", "category": "Produce", "aisle": "Produce", "aliases": ["navel oranges", "valencia oranges", "citrus"]},
            {"name": "Lemons", "category": "Produce", "aisle": "Produce", "aliases": ["fresh lemons", "citrus"]},
            {"name": "Limes", "category": "Produce", "aisle": "Produce", "aliases": ["fresh limes", "citrus"]},
            {"name": "Grapes", "category": "Produce", "aisle": "Produce", "aliases": ["red grapes", "green grapes", "seedless grapes"]},
            {"name": "Strawberries", "category": "Produce", "aisle": "Produce", "aliases": ["fresh strawberries", "berries"]},
            {"name": "Blueberries", "category": "Produce", "aisle": "Produce", "aliases": ["fresh blueberries", "berries"]},
            {"name": "Raspberries", "category": "Produce", "aisle": "Produce", "aliases": ["fresh raspberries", "berries"]},
            {"name": "Blackberries", "category": "Produce", "aisle": "Produce", "aliases": ["fresh blackberries", "berries"]},
            {"name": "Pineapple", "category": "Produce", "aisle": "Produce", "aliases": ["fresh pineapple", "whole pineapple"]},
            {"name": "Mango", "category": "Produce", "aisle": "Produce", "aliases": ["fresh mango", "ripe mango"]},
            {"name": "Avocado", "category": "Produce", "aisle": "Produce", "aliases": ["fresh avocado", "ripe avocado"]},
            {"name": "Kiwi", "category": "Produce", "aisle": "Produce", "aliases": ["kiwi fruit", "fresh kiwi"]},
            {"name": "Peaches", "category": "Produce", "aisle": "Produce", "aliases": ["fresh peaches", "ripe peaches"]},
            {"name": "Pears", "category": "Produce", "aisle": "Produce", "aliases": ["fresh pears", "anjou pears"]},
            
            # Vegetables
            {"name": "Carrots", "category": "Produce", "aisle": "Produce", "aliases": ["baby carrots", "fresh carrots"]},
            {"name": "Lettuce", "category": "Produce", "aisle": "Produce", "aliases": ["iceberg lettuce", "romaine lettuce", "green lettuce"]},
            {"name": "Spinach", "category": "Produce", "aisle": "Produce", "aliases": ["fresh spinach", "baby spinach", "leafy greens"]},
            {"name": "Broccoli", "category": "Produce", "aisle": "Produce", "aliases": ["fresh broccoli", "broccoli crowns"]},
            {"name": "Cauliflower", "category": "Produce", "aisle": "Produce", "aliases": ["fresh cauliflower", "cauliflower head"]},
            {"name": "Bell Peppers", "category": "Produce", "aisle": "Produce", "aliases": ["red peppers", "green peppers", "yellow peppers", "peppers"]},
            {"name": "Onions", "category": "Produce", "aisle": "Produce", "aliases": ["yellow onions", "red onions", "white onions"]},
            {"name": "Garlic", "category": "Produce", "aisle": "Produce", "aliases": ["fresh garlic", "garlic bulbs"]},
            {"name": "Tomatoes", "category": "Produce", "aisle": "Produce", "aliases": ["fresh tomatoes", "cherry tomatoes", "roma tomatoes"]},
            {"name": "Cucumbers", "category": "Produce", "aisle": "Produce", "aliases": ["fresh cucumbers", "english cucumbers"]},
            {"name": "Celery", "category": "Produce", "aisle": "Produce", "aliases": ["fresh celery", "celery stalks"]},
            {"name": "Mushrooms", "category": "Produce", "aisle": "Produce", "aliases": ["white mushrooms", "button mushrooms", "portobello"]},
            {"name": "Potatoes", "category": "Produce", "aisle": "Produce", "aliases": ["russet potatoes", "red potatoes", "sweet potatoes"]},
            
            # DAIRY SECTION
            {"name": "Milk", "category": "Dairy", "aisle": "Dairy", "aliases": ["whole milk", "2% milk", "skim milk", "1% milk", "almond milk", "oat milk"]},
            {"name": "Cheese", "category": "Dairy", "aisle": "Dairy", "aliases": ["cheddar cheese", "mozzarella", "swiss cheese", "american cheese"]},
            {"name": "Yogurt", "category": "Dairy", "aisle": "Dairy", "aliases": ["greek yogurt", "vanilla yogurt", "strawberry yogurt"]},
            {"name": "Butter", "category": "Dairy", "aisle": "Dairy", "aliases": ["salted butter", "unsalted butter", "margarine"]},
            {"name": "Eggs", "category": "Dairy", "aisle": "Dairy", "aliases": ["chicken eggs", "large eggs", "dozen eggs"]},
            {"name": "Cream Cheese", "category": "Dairy", "aisle": "Dairy", "aliases": ["philadelphia cream cheese", "soft cheese"]},
            {"name": "Sour Cream", "category": "Dairy", "aisle": "Dairy", "aliases": ["sour cream", "dairy cream"]},
            {"name": "Heavy Cream", "category": "Dairy", "aisle": "Dairy", "aliases": ["whipping cream", "cooking cream"]},
            
            # MEAT & SEAFOOD
            {"name": "Chicken Breast", "category": "Meat", "aisle": "Deli", "aliases": ["chicken", "boneless chicken", "skinless chicken"]},
            {"name": "Ground Beef", "category": "Meat", "aisle": "Deli", "aliases": ["hamburger meat", "beef", "ground chuck"]},
            {"name": "Pork Chops", "category": "Meat", "aisle": "Deli", "aliases": ["pork", "bone-in pork chops"]},
            {"name": "Bacon", "category": "Meat", "aisle": "Deli", "aliases": ["sliced bacon", "thick cut bacon"]},
            {"name": "Ham", "category": "Meat", "aisle": "Deli", "aliases": ["sliced ham", "deli ham", "honey ham"]},
            {"name": "Turkey", "category": "Meat", "aisle": "Deli", "aliases": ["sliced turkey", "deli turkey", "turkey breast"]},
            {"name": "Salmon", "category": "Seafood", "aisle": "Deli", "aliases": ["fresh salmon", "salmon fillets"]},
            {"name": "Shrimp", "category": "Seafood", "aisle": "Deli", "aliases": ["fresh shrimp", "frozen shrimp"]},
            {"name": "Tuna", "category": "Seafood", "aisle": "Deli", "aliases": ["fresh tuna", "tuna steaks"]},
            
            # BAKERY SECTION
            {"name": "Bread", "category": "Bakery", "aisle": "Bakery", "aliases": ["white bread", "wheat bread", "whole grain bread", "loaf"]},
            {"name": "Bagels", "category": "Bakery", "aisle": "Bakery", "aliases": ["everything bagels", "plain bagels", "sesame bagels"]},
            {"name": "Croissants", "category": "Bakery", "aisle": "Bakery", "aliases": ["butter croissants", "fresh croissants"]},
            {"name": "Muffins", "category": "Bakery", "aisle": "Bakery", "aliases": ["blueberry muffins", "chocolate chip muffins"]},
            {"name": "Donuts", "category": "Bakery", "aisle": "Bakery", "aliases": ["glazed donuts", "chocolate donuts", "doughnuts"]},
            {"name": "Cookies", "category": "Bakery", "aisle": "Bakery", "aliases": ["chocolate chip cookies", "sugar cookies"]},
            {"name": "Cake", "category": "Bakery", "aisle": "Bakery", "aliases": ["birthday cake", "sheet cake", "cupcakes"]},
            
            # PANTRY/DRY GOODS - AISLE 1
            {"name": "Rice", "category": "Pantry", "aisle": "Aisle 1", "aliases": ["white rice", "brown rice", "jasmine rice", "basmati rice"]},
            {"name": "Pasta", "category": "Pantry", "aisle": "Aisle 1", "aliases": ["spaghetti", "penne", "macaroni", "noodles"]},
            {"name": "Quinoa", "category": "Pantry", "aisle": "Aisle 1", "aliases": ["quinoa grain", "organic quinoa"]},
            {"name": "Flour", "category": "Baking", "aisle": "Aisle 1", "aliases": ["all-purpose flour", "wheat flour", "baking flour"]},
            {"name": "Sugar", "category": "Baking", "aisle": "Aisle 1", "aliases": ["white sugar", "brown sugar", "granulated sugar"]},
            {"name": "Salt", "category": "Spices", "aisle": "Aisle 1", "aliases": ["table salt", "sea salt", "kosher salt"]},
            {"name": "Black Pepper", "category": "Spices", "aisle": "Aisle 1", "aliases": ["pepper", "ground pepper", "peppercorns"]},
            {"name": "Olive Oil", "category": "Cooking Oil", "aisle": "Aisle 1", "aliases": ["extra virgin olive oil", "cooking oil"]},
            {"name": "Vegetable Oil", "category": "Cooking Oil", "aisle": "Aisle 1", "aliases": ["canola oil", "cooking oil"]},
            {"name": "Vinegar", "category": "Condiments", "aisle": "Aisle 1", "aliases": ["white vinegar", "apple cider vinegar"]},
            
            # BREAKFAST - AISLE 1
            {"name": "Cereal", "category": "Breakfast", "aisle": "Aisle 1", "aliases": ["breakfast cereal", "cornflakes", "cheerios", "granola"]},
            {"name": "Oatmeal", "category": "Breakfast", "aisle": "Aisle 1", "aliases": ["oats", "rolled oats", "quick oats", "instant oatmeal"]},
            {"name": "Pancake Mix", "category": "Breakfast", "aisle": "Aisle 1", "aliases": ["pancake flour", "waffle mix", "bisquick"]},
            {"name": "Syrup", "category": "Breakfast", "aisle": "Aisle 1", "aliases": ["maple syrup", "pancake syrup", "breakfast syrup"]},
            {"name": "Peanut Butter", "category": "Breakfast", "aisle": "Aisle 1", "aliases": ["chunky peanut butter", "smooth peanut butter", "jif"]},
            {"name": "Jelly", "category": "Breakfast", "aisle": "Aisle 1", "aliases": ["jam", "grape jelly", "strawberry jam", "preserves"]},
            
            # CANNED GOODS - AISLE 2
            {"name": "Canned Tomatoes", "category": "Canned Goods", "aisle": "Aisle 2", "aliases": ["diced tomatoes", "crushed tomatoes", "tomato sauce"]},
            {"name": "Canned Beans", "category": "Canned Goods", "aisle": "Aisle 2", "aliases": ["black beans", "kidney beans", "chickpeas", "garbanzo beans"]},
            {"name": "Soup", "category": "Canned Goods", "aisle": "Aisle 2", "aliases": ["chicken soup", "vegetable soup", "tomato soup", "canned soup"]},
            {"name": "Tuna", "category": "Canned Goods", "aisle": "Aisle 2", "aliases": ["canned tuna", "tuna fish", "chunk tuna"]},
            {"name": "Chicken Broth", "category": "Canned Goods", "aisle": "Aisle 2", "aliases": ["broth", "stock", "chicken stock", "vegetable broth"]},
            {"name": "Coconut Milk", "category": "Canned Goods", "aisle": "Aisle 2", "aliases": ["canned coconut milk", "coconut cream"]},
            {"name": "Corn", "category": "Canned Goods", "aisle": "Aisle 2", "aliases": ["canned corn", "sweet corn", "kernel corn"]},
            {"name": "Green Beans", "category": "Canned Goods", "aisle": "Aisle 2", "aliases": ["canned green beans", "string beans"]},
            
            # SNACKS - AISLE 3
            {"name": "Chips", "category": "Snacks", "aisle": "Aisle 3", "aliases": ["potato chips", "tortilla chips", "corn chips", "lays", "doritos"]},
            {"name": "Pretzels", "category": "Snacks", "aisle": "Aisle 3", "aliases": ["salted pretzels", "pretzel sticks"]},
            {"name": "Popcorn", "category": "Snacks", "aisle": "Aisle 3", "aliases": ["microwave popcorn", "kettle corn", "movie popcorn"]},
            {"name": "Crackers", "category": "Snacks", "aisle": "Aisle 3", "aliases": ["saltines", "ritz crackers", "graham crackers"]},
            {"name": "Nuts", "category": "Snacks", "aisle": "Aisle 3", "aliases": ["peanuts", "almonds", "cashews", "mixed nuts"]},
            {"name": "Trail Mix", "category": "Snacks", "aisle": "Aisle 3", "aliases": ["mixed nuts", "nut mix", "hiking mix"]},
            {"name": "Granola Bars", "category": "Snacks", "aisle": "Aisle 3", "aliases": ["protein bars", "energy bars", "cereal bars"]},
            {"name": "Candy", "category": "Snacks", "aisle": "Aisle 3", "aliases": ["chocolate", "gummy bears", "hard candy", "sweets"]},
            
            # BEVERAGES - AISLE 4
            {"name": "Water", "category": "Beverages", "aisle": "Aisle 4", "aliases": ["bottled water", "spring water", "sparkling water"]},
            {"name": "Soda", "category": "Beverages", "aisle": "Aisle 4", "aliases": ["soft drinks", "cola", "pepsi", "coke", "sprite", "diet coke"]},
            {"name": "Juice", "category": "Beverages", "aisle": "Aisle 4", "aliases": ["orange juice", "apple juice", "cranberry juice", "fruit juice"]},
            {"name": "Coffee", "category": "Beverages", "aisle": "Aisle 4", "aliases": ["ground coffee", "coffee beans", "instant coffee", "starbucks"]},
            {"name": "Tea", "category": "Beverages", "aisle": "Aisle 4", "aliases": ["tea bags", "green tea", "black tea", "herbal tea"]},
            {"name": "Energy Drinks", "category": "Beverages", "aisle": "Aisle 4", "aliases": ["red bull", "monster", "sports drinks"]},
            {"name": "Beer", "category": "Alcoholic Beverages", "aisle": "Aisle 4", "aliases": ["craft beer", "light beer", "domestic beer"]},
            {"name": "Wine", "category": "Alcoholic Beverages", "aisle": "Aisle 4", "aliases": ["red wine", "white wine", "champagne"]},
            
            # FROZEN FOODS - AISLE 5
            {"name": "Ice Cream", "category": "Frozen", "aisle": "Aisle 5", "aliases": ["vanilla ice cream", "chocolate ice cream", "frozen dessert", "gelato"]},
            {"name": "Frozen Pizza", "category": "Frozen", "aisle": "Aisle 5", "aliases": ["pizza", "pepperoni pizza", "cheese pizza"]},
            {"name": "Frozen Vegetables", "category": "Frozen", "aisle": "Aisle 5", "aliases": ["frozen peas", "frozen corn", "frozen broccoli"]},
            {"name": "Frozen Fruit", "category": "Frozen", "aisle": "Aisle 5", "aliases": ["frozen berries", "frozen strawberries", "frozen mango"]},
            {"name": "Frozen Meals", "category": "Frozen", "aisle": "Aisle 5", "aliases": ["tv dinners", "frozen dinners", "lean cuisine", "hungry man"]},
            {"name": "French Fries", "category": "Frozen", "aisle": "Aisle 5", "aliases": ["frozen fries", "potato fries", "oven fries"]},
            {"name": "Frozen Chicken", "category": "Frozen", "aisle": "Aisle 5", "aliases": ["frozen chicken nuggets", "chicken tenders"]},
            {"name": "Frozen Waffles", "category": "Frozen", "aisle": "Aisle 5", "aliases": ["eggo waffles", "breakfast waffles"]},
            
            # HEALTH & BEAUTY
            {"name": "Shampoo", "category": "Health & Beauty", "aisle": "Pharmacy", "aliases": ["hair shampoo", "head & shoulders", "pantene"]},
            {"name": "Conditioner", "category": "Health & Beauty", "aisle": "Pharmacy", "aliases": ["hair conditioner", "moisturizer"]},
            {"name": "Toothpaste", "category": "Health & Beauty", "aisle": "Pharmacy", "aliases": ["crest", "colgate", "dental care"]},
            {"name": "Toothbrush", "category": "Health & Beauty", "aisle": "Pharmacy", "aliases": ["electric toothbrush", "manual toothbrush"]},
            {"name": "Soap", "category": "Health & Beauty", "aisle": "Pharmacy", "aliases": ["body soap", "hand soap", "bar soap", "dove"]},
            {"name": "Deodorant", "category": "Health & Beauty", "aisle": "Pharmacy", "aliases": ["antiperspirant", "body spray"]},
            {"name": "Vitamins", "category": "Health & Beauty", "aisle": "Pharmacy", "aliases": ["multivitamins", "vitamin c", "supplements"]},
            {"name": "Pain Relief", "category": "Health & Beauty", "aisle": "Pharmacy", "aliases": ["aspirin", "ibuprofen", "tylenol", "advil"]},
            
            # HOUSEHOLD ITEMS
            {"name": "Toilet Paper", "category": "Household", "aisle": "Household", "aliases": ["bathroom tissue", "tp", "charmin"]},
            {"name": "Paper Towels", "category": "Household", "aisle": "Household", "aliases": ["kitchen towels", "bounty"]},
            {"name": "Laundry Detergent", "category": "Household", "aisle": "Household", "aliases": ["washing detergent", "tide", "fabric cleaner"]},
            {"name": "Dish Soap", "category": "Household", "aisle": "Household", "aliases": ["dishwashing liquid", "dawn", "kitchen cleaner"]},
            {"name": "Trash Bags", "category": "Household", "aisle": "Household", "aliases": ["garbage bags", "waste bags", "hefty bags"]},
            {"name": "Aluminum Foil", "category": "Household", "aisle": "Household", "aliases": ["foil", "cooking foil", "reynolds wrap"]},
            {"name": "Plastic Wrap", "category": "Household", "aisle": "Household", "aliases": ["saran wrap", "food wrap", "cling film"]},
            
            # BABY CARE
            {"name": "Diapers", "category": "Baby Care", "aisle": "Baby Care", "aliases": ["baby diapers", "pampers", "huggies"]},
            {"name": "Baby Food", "category": "Baby Care", "aisle": "Baby Care", "aliases": ["baby formula", "gerber", "infant food"]},
            {"name": "Baby Wipes", "category": "Baby Care", "aisle": "Baby Care", "aliases": ["wet wipes", "cleaning wipes"]},
            
            # PET CARE
            {"name": "Dog Food", "category": "Pet Care", "aisle": "Pet Care", "aliases": ["dry dog food", "wet dog food", "puppy food"]},
            {"name": "Cat Food", "category": "Pet Care", "aisle": "Pet Care", "aliases": ["dry cat food", "wet cat food", "kitten food"]},
            {"name": "Cat Litter", "category": "Pet Care", "aisle": "Pet Care", "aliases": ["kitty litter", "clumping litter"]},
            {"name": "Dog Treats", "category": "Pet Care", "aisle": "Pet Care", "aliases": ["dog biscuits", "training treats"]},
        ]
        
        for product_data in default_products:
            product = Product(
                name=product_data["name"],
                category=product_data["category"],
                aisle=product_data["aisle"]
            )
            
            for alias in product_data.get("aliases", []):
                product.add_alias(alias)
            
            self.products[product.name] = product
    
    def _organize_by_categories(self):
        """Organize products by category for easier searching."""
        self.categories.clear()
        
        for product in self.products.values():
            if product.category not in self.categories:
                self.categories[product.category] = []
            self.categories[product.category].append(product)
    
    def search_products(self, query: str) -> List[Product]:
        """
        Search for products matching the query.
        
        Args:
            query: Search query (can include command words like 'find')
            
        Returns:
            List of matching products, sorted by relevance
        """
        # Clean the query
        cleaned_query = self._clean_query(query)
        
        if not cleaned_query:
            return []
        
        # Find matching products with confidence scores
        matches = []
        
        for product in self.products.values():
            confidence = product.matches_query(cleaned_query)
            if confidence > 0:
                matches.append((product, confidence))
        
        # Sort by confidence (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the products
        return [match[0] for match in matches]
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize the search query."""
        query = query.lower().strip()
        
        # Remove command words
        command_words = ['find', 'where is', 'locate', 'looking for', 'search for', 'get me', 'i need']
        for command in command_words:
            if query.startswith(command):
                query = query[len(command):].strip()
        
        # Remove articles and common words
        stop_words = ['the', 'a', 'an', 'some', 'any']
        words = query.split()
        filtered_words = [word for word in words if word not in stop_words]
        
        return ' '.join(filtered_words) if filtered_words else query
    
    def get_product_guidance(self, product: Product) -> str:
        """
        Generate voice guidance for finding a product.
        
        Args:
            product: The product to provide guidance for
            
        Returns:
            Voice guidance string
        """
        guidance = f"I found {product.name}. "
        
        if product.aisle:
            guidance += f"You can find it in {product.aisle}. "
        
        if product.category:
            guidance += f"It's in the {product.category} section. "
        
        if product.description:
            guidance += f"{product.description} "
        
        return guidance
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Get all products in a specific category."""
        return self.categories.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        """Get all available product categories."""
        return list(self.categories.keys())
    
    def suggest_alternatives(self, product_name: str) -> List[Product]:
        """Suggest alternative products when a search fails."""
        # Try to find products in the same category or with similar names
        suggestions = []
        
        # Look for partial matches
        for product in self.products.values():
            if any(word in product.name.lower() for word in product_name.lower().split()):
                suggestions.append(product)
        
        return suggestions[:5]  # Return top 5 suggestions