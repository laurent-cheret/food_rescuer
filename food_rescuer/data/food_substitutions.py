# food_rescuer/data/food_substitutions.py
# Knowledge base for ingredient substitutions

import os
import json
from collections import defaultdict

class SubstitutionKnowledgeBase:
    """Manages knowledge about ingredient substitutions"""
    
    # Update your SubstitutionKnowledgeBase class initialization to load data-derived substitutions

    def __init__(self, data_dir=None):
        """Initialize the substitution knowledge base with both curated and data-derived substitutions"""
        self.substitutions = {}
        self.categories = {}
        self.category_to_ingredients = defaultdict(list)
        
        # Set default data directory if not provided
        if data_dir is None:
            # Get the directory where this script is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the project root
            project_dir = os.path.dirname(current_dir)
            data_dir = os.path.join(project_dir, 'data', 'processed')
        
        # Path for saving/loading substitution data
        self.substitutions_path = os.path.join(data_dir, 'substitutions.json')
        self.categories_path = os.path.join(data_dir, 'ingredient_categories.json')
        self.data_derived_path = os.path.join(data_dir, 'data_derived_substitutions.json')
        
        # Initialize the knowledge base
        self._initialize_categories()
        self._initialize_substitutions()
        self._load_data_derived_substitutions()
        
        # Save the initialized data if it doesn't exist
        if not os.path.exists(self.substitutions_path):
            self.save()

    # Add this new method to load data-derived substitutions
    def _load_data_derived_substitutions(self):
        """Load substitutions derived from data analysis"""
        if os.path.exists(self.data_derived_path):
            try:
                with open(self.data_derived_path, 'r') as f:
                    data_derived = json.load(f)
                    
                    # Merge with existing substitutions
                    for ingredient, substitutes in data_derived.items():
                        # Normalize ingredient name
                        ingredient_lower = ingredient.lower()
                        
                        # Initialize if needed
                        if ingredient_lower not in self.substitutions:
                            self.substitutions[ingredient_lower] = []
                        
                        # Add each substitute if not already present
                        existing_subs = set(sub['substitute'].lower() for sub in self.substitutions[ingredient_lower])
                        
                        for sub in substitutes:
                            if sub['substitute'].lower() not in existing_subs:
                                # Convert to our standard format
                                self.substitutions[ingredient_lower].append({
                                    'substitute': sub['substitute'],
                                    'ratio': sub.get('ratio', 1.0),
                                    'notes': sub.get('notes', '')
                                })
                                existing_subs.add(sub['substitute'].lower())
                    
                    print(f"Loaded {len(data_derived)} ingredients with data-derived substitutions")
            except Exception as e:
                print(f"Error loading data-derived substitutions: {e}")

    # Add new method to get substitutions for a recipe ingredient
    def get_substitutions_for_recipe_ingredient(self, ingredient, available_ingredients=None):
        """
        Get suitable substitutions for a specific recipe ingredient
        
        Args:
            ingredient: The ingredient to find substitutes for
            available_ingredients: Optional list of available ingredients to filter by
            
        Returns:
            list: Suitable substitutions
        """
        substitutes = self.get_substitutions(ingredient)
        
        # If no substitutes found, try to clean up the ingredient name
        # (recipes often have quantities or forms like "chopped onions")
        if not substitutes:
            # Try to extract the base ingredient
            import re
            base_ingredient_match = re.search(r'(\b[a-z]+\b)(?:\s+[a-z]+)*$', ingredient.lower())
            if base_ingredient_match:
                base_ingredient = base_ingredient_match.group(1)
                substitutes = self.get_substitutions(base_ingredient)
        
        # If available ingredients provided, filter to those
        if available_ingredients and substitutes:
            available_lower = [ing.lower() for ing in available_ingredients]
            available_substitutes = []
            
            for sub in substitutes:
                if sub['substitute'].lower() in available_lower:
                    available_substitutes.append(sub)
            
            # If we have available substitutes, use those
            if available_substitutes:
                return available_substitutes
        
        return substitutes
    
    def _initialize_categories(self):
        """Set up ingredient categories"""
        if os.path.exists(self.categories_path):
            # Load existing categories if available
            with open(self.categories_path, 'r') as f:
                data = json.load(f)
                self.categories = data.get('categories', {})
                self.category_to_ingredients = defaultdict(list, data.get('category_to_ingredients', {}))
        else:
            # Define standard ingredient categories
            self.categories = {
                # Fats and oils
                'butter': 'fats',
                'olive oil': 'fats',
                'vegetable oil': 'fats',
                'coconut oil': 'fats',
                'shortening': 'fats',
                'margarine': 'fats',
                'ghee': 'fats',
                'lard': 'fats',
                
                # Dairy
                'milk': 'dairy',
                'heavy cream': 'dairy',
                'half and half': 'dairy',
                'yogurt': 'dairy',
                'sour cream': 'dairy',
                'buttermilk': 'dairy',
                'evaporated milk': 'dairy',
                'condensed milk': 'dairy',
                'cream cheese': 'dairy',
                
                # Proteins
                'eggs': 'proteins',
                'chicken': 'proteins',
                'beef': 'proteins',
                'pork': 'proteins',
                'tofu': 'proteins',
                'tempeh': 'proteins',
                'seitan': 'proteins',
                
                # Sweeteners
                'sugar': 'sweeteners',
                'brown sugar': 'sweeteners',
                'honey': 'sweeteners',
                'maple syrup': 'sweeteners',
                'agave nectar': 'sweeteners',
                'molasses': 'sweeteners',
                'corn syrup': 'sweeteners',
                
                # Flours and starches
                'flour': 'flours',
                'all-purpose flour': 'flours',
                'bread flour': 'flours',
                'cake flour': 'flours',
                'wheat flour': 'flours',
                'cornstarch': 'starches',
                'potato starch': 'starches',
                'tapioca starch': 'starches',
                'arrowroot': 'starches',
                
                # Leavening agents
                'baking powder': 'leavening',
                'baking soda': 'leavening',
                'yeast': 'leavening',
                
                # Acids
                'vinegar': 'acids',
                'lemon juice': 'acids',
                'lime juice': 'acids',
                'orange juice': 'acids',
                'wine': 'acids',
                
                # Herbs and spices
                'salt': 'spices',
                'black pepper': 'spices',
                'pepper': 'spices',
                'oregano': 'herbs',
                'basil': 'herbs',
                'thyme': 'herbs',
                'rosemary': 'herbs',
                'parsley': 'herbs',
                'cilantro': 'herbs',
                'mint': 'herbs',
                'dill': 'herbs',
                'chives': 'herbs',
                
                # Vegetables
                'onion': 'vegetables',
                'garlic': 'vegetables',
                'garlic cloves': 'vegetables',
                'carrots': 'vegetables',
                'celery': 'vegetables',
                'bell pepper': 'vegetables',
                'tomatoes': 'vegetables',
                'potatoes': 'vegetables',
                
                # Fruits
                'apples': 'fruits',
                'bananas': 'fruits',
                'berries': 'fruits',
                'strawberries': 'fruits',
                'lemons': 'fruits',
                'limes': 'fruits',
                'oranges': 'fruits',
                
                # Nuts and seeds
                'almonds': 'nuts',
                'walnuts': 'nuts',
                'peanuts': 'nuts',
                'cashews': 'nuts',
                'pecans': 'nuts',
                'pine nuts': 'nuts',
                'sunflower seeds': 'seeds',
                'pumpkin seeds': 'seeds',
                'flax seeds': 'seeds',
                'chia seeds': 'seeds',
                
                # Alcohols
                'white wine': 'alcohols',
                'red wine': 'alcohols',
                'vodka': 'alcohols',
                'rum': 'alcohols',
                'brandy': 'alcohols',
                'bourbon': 'alcohols',
                
                # Stocks and broths
                'chicken broth': 'broths',
                'beef broth': 'broths',
                'vegetable broth': 'broths',
                'chicken stock': 'broths',
                'beef stock': 'broths',
                'bouillon': 'broths',
            }
            
            # Populate category_to_ingredients mapping
            for ingredient, category in self.categories.items():
                self.category_to_ingredients[category].append(ingredient)
    
    def _initialize_substitutions(self):
        """Initialize the substitution knowledge base"""
        if os.path.exists(self.substitutions_path):
            # Load existing substitutions if available
            with open(self.substitutions_path, 'r') as f:
                self.substitutions = json.load(f)
        else:
            # Initialize with a set of common substitutions
            # Format: ingredient -> list of possible substitutions with adjustment notes
            self.substitutions = {
                # Fats and oils
                "butter": [
                    {"substitute": "olive oil", "ratio": 0.75, "notes": "Works well in savory dishes"},
                    {"substitute": "coconut oil", "ratio": 1.0, "notes": "Good for baking"},
                    {"substitute": "margarine", "ratio": 1.0, "notes": "Direct substitute"},
                    {"substitute": "vegetable oil", "ratio": 0.75, "notes": "Good for baking"}
                ],
                "olive oil": [
                    {"substitute": "vegetable oil", "ratio": 1.0, "notes": "Neutral flavor"},
                    {"substitute": "coconut oil", "ratio": 1.0, "notes": "Will add coconut flavor"},
                    {"substitute": "butter", "ratio": 1.33, "notes": "Use 1⅓ the amount"}
                ],
                "vegetable oil": [
                    {"substitute": "olive oil", "ratio": 1.0, "notes": "Will add olive flavor"},
                    {"substitute": "coconut oil", "ratio": 1.0, "notes": "Will add coconut flavor"},
                    {"substitute": "butter", "ratio": 1.33, "notes": "Use 1⅓ the amount"}
                ],
                
                # Dairy
                "milk": [
                    {"substitute": "almond milk", "ratio": 1.0, "notes": "Good for most recipes"},
                    {"substitute": "soy milk", "ratio": 1.0, "notes": "Good protein content"},
                    {"substitute": "oat milk", "ratio": 1.0, "notes": "Creamy texture, good for baking"},
                    {"substitute": "yogurt", "ratio": 0.75, "notes": "Thin with water if needed"},
                    {"substitute": "water", "ratio": 1.0, "notes": "Only use in recipes where milk is not a key ingredient"}
                ],
                "heavy cream": [
                    {"substitute": "milk", "ratio": 1.0, "notes": "Add 2 tbsp butter per cup of milk"},
                    {"substitute": "evaporated milk", "ratio": 1.0, "notes": "Direct substitute"},
                    {"substitute": "yogurt", "ratio": 1.0, "notes": "Good for baking and sauces"},
                    {"substitute": "coconut cream", "ratio": 1.0, "notes": "Good for desserts and curries"}
                ],
                "sour cream": [
                    {"substitute": "yogurt", "ratio": 1.0, "notes": "Plain, full-fat works best"},
                    {"substitute": "buttermilk", "ratio": 1.0, "notes": "For baking"},
                    {"substitute": "cream cheese", "ratio": 1.0, "notes": "Soften and add a bit of milk"}
                ],
                "yogurt": [
                    {"substitute": "sour cream", "ratio": 1.0, "notes": "Direct substitute"},
                    {"substitute": "buttermilk", "ratio": 1.0, "notes": "For baking"},
                    {"substitute": "cottage cheese", "ratio": 1.0, "notes": "Blend until smooth first"}
                ],
                "cream cheese": [
                    {"substitute": "mascarpone", "ratio": 1.0, "notes": "Slightly sweeter"},
                    {"substitute": "ricotta", "ratio": 1.0, "notes": "Blend with a bit of cream for smoothness"},
                    {"substitute": "cottage cheese", "ratio": 1.0, "notes": "Blend until smooth"}
                ],
                
                # Eggs
                "eggs": [
                    {"substitute": "applesauce", "ratio": 0.25, "unit": "cup", "notes": "Use 1/4 cup per egg for baking"},
                    {"substitute": "mashed banana", "ratio": 0.5, "unit": "medium", "notes": "1/2 banana per egg for baking"},
                    {"substitute": "yogurt", "ratio": 0.25, "unit": "cup", "notes": "1/4 cup per egg for baking"},
                    {"substitute": "flax seeds", "ratio": 1.0, "unit": "tbsp", "notes": "Mix 1 tbsp ground flax with 3 tbsp water per egg"}
                ],
                
                # Sweeteners
                "sugar": [
                    {"substitute": "brown sugar", "ratio": 1.0, "notes": "Will add molasses flavor"},
                    {"substitute": "honey", "ratio": 0.75, "notes": "Reduce other liquids by 1/4 cup per cup of honey"},
                    {"substitute": "maple syrup", "ratio": 0.75, "notes": "Reduce other liquids by 3 tbsp per cup"}
                ],
                "brown sugar": [
                    {"substitute": "white sugar", "ratio": 1.0, "notes": "Add 1 tbsp molasses per cup"},
                    {"substitute": "honey", "ratio": 0.75, "notes": "Reduce other liquids by 1/4 cup per cup of honey"},
                    {"substitute": "maple syrup", "ratio": 0.75, "notes": "Reduce other liquids by 3 tbsp per cup"}
                ],
                "honey": [
                    {"substitute": "maple syrup", "ratio": 1.0, "notes": "Direct substitute"},
                    {"substitute": "agave nectar", "ratio": 1.0, "notes": "Direct substitute"},
                    {"substitute": "sugar", "ratio": 1.25, "notes": "Add 1/4 cup liquid per cup of sugar"}
                ],
                
                # Flours and Starches
                "all-purpose flour": [
                    {"substitute": "bread flour", "ratio": 1.0, "notes": "Will result in chewier texture"},
                    {"substitute": "cake flour", "ratio": 1.0, "notes": "Will result in lighter texture"},
                    {"substitute": "whole wheat flour", "ratio": 0.75, "notes": "Use 3/4 cup whole wheat + 1/4 cup white per cup"}
                ],
                "flour": [
                    {"substitute": "cornstarch", "ratio": 0.5, "notes": "For thickening only"},
                    {"substitute": "almond flour", "ratio": 1.0, "notes": "For gluten-free baking"},
                    {"substitute": "oat flour", "ratio": 1.0, "notes": "For gluten-free baking"}
                ],
                "cornstarch": [
                    {"substitute": "flour", "ratio": 2.0, "notes": "For thickening, use twice as much"},
                    {"substitute": "arrowroot", "ratio": 1.0, "notes": "Direct substitute for thickening"},
                    {"substitute": "potato starch", "ratio": 1.0, "notes": "Direct substitute for thickening"}
                ],
                
                # Leavening Agents
                "baking powder": [
                    {"substitute": "baking soda", "ratio": 0.25, "notes": "Use 1/4 tsp baking soda + 1/2 tsp cream of tartar"},
                    {"substitute": "yeast", "ratio": 0.5, "notes": "Only for certain recipes, changes texture significantly"}
                ],
                "baking soda": [
                    {"substitute": "baking powder", "ratio": 3.0, "notes": "Use 3 times as much, omit or reduce acidic ingredients"}
                ],
                "yeast": [
                    {"substitute": "baking powder", "ratio": 1.0, "unit": "tsp", "notes": "Use 1 tsp per 1/4 oz yeast, texture will be different"}
                ],
                
                # Acids
                "vinegar": [
                    {"substitute": "lemon juice", "ratio": 1.0, "notes": "Direct substitute"},
                    {"substitute": "lime juice", "ratio": 1.0, "notes": "Direct substitute"},
                    {"substitute": "white wine", "ratio": 1.0, "notes": "For cooking"}
                ],
                "lemon juice": [
                    {"substitute": "vinegar", "ratio": 0.5, "notes": "Use half as much"},
                    {"substitute": "lime juice", "ratio": 1.0, "notes": "Direct substitute"},
                    {"substitute": "orange juice", "ratio": 1.0, "notes": "Will be sweeter"}
                ],
                
                # Herbs and Spices
                "fresh herbs": [
                    {"substitute": "dried herbs", "ratio": 0.33, "notes": "Use 1/3 the amount of dried herbs"}
                ],
                "dried herbs": [
                    {"substitute": "fresh herbs", "ratio": 3.0, "notes": "Use 3 times as much fresh herbs"}
                ],
                
                # Vegetables
                "onion": [
                    {"substitute": "shallots", "ratio": 1.0, "notes": "More delicate flavor"},
                    {"substitute": "leeks", "ratio": 1.0, "notes": "Milder flavor"},
                    {"substitute": "green onions", "ratio": 1.0, "notes": "Milder flavor"},
                    {"substitute": "onion powder", "ratio": 1.0, "unit": "tbsp", "notes": "1 tbsp per medium onion"}
                ],
                "garlic": [
                    {"substitute": "garlic powder", "ratio": 0.125, "unit": "tsp", "notes": "1/8 tsp per clove"},
                    {"substitute": "shallots", "ratio": 1.0, "notes": "Milder flavor"},
                    {"substitute": "onion", "ratio": 1.0, "notes": "Different flavor but similar function"}
                ],
                "tomatoes": [
                    {"substitute": "canned tomatoes", "ratio": 1.0, "notes": "Drain if fresh is called for"},
                    {"substitute": "tomato paste", "ratio": 0.25, "notes": "Use 1/4 the amount + water"},
                    {"substitute": "bell peppers", "ratio": 1.0, "notes": "For texture in salads"}
                ],
                
                # Stocks and Broths
                "chicken broth": [
                    {"substitute": "vegetable broth", "ratio": 1.0, "notes": "Direct substitute"},
                    {"substitute": "beef broth", "ratio": 1.0, "notes": "Stronger flavor"},
                    {"substitute": "bouillon cube", "ratio": 1.0, "unit": "cube", "notes": "1 cube per cup of water"}
                ],
                "beef broth": [
                    {"substitute": "vegetable broth", "ratio": 1.0, "notes": "Direct substitute"},
                    {"substitute": "chicken broth", "ratio": 1.0, "notes": "Milder flavor"},
                    {"substitute": "bouillon cube", "ratio": 1.0, "unit": "cube", "notes": "1 cube per cup of water"}
                ],
                "vegetable broth": [
                    {"substitute": "chicken broth", "ratio": 1.0, "notes": "Not vegetarian"},
                    {"substitute": "water", "ratio": 1.0, "notes": "Add extra herbs and spices"},
                    {"substitute": "bouillon cube", "ratio": 1.0, "unit": "cube", "notes": "1 cube per cup of water"}
                ],
                
                # Alcohols
                "white wine": [
                    {"substitute": "chicken broth", "ratio": 1.0, "notes": "For savory dishes"},
                    {"substitute": "white grape juice", "ratio": 1.0, "notes": "Add 1 tbsp vinegar per cup"},
                    {"substitute": "water", "ratio": 1.0, "notes": "Add 1 tbsp vinegar or lemon juice per cup"}
                ],
                "red wine": [
                    {"substitute": "beef broth", "ratio": 1.0, "notes": "For savory dishes"},
                    {"substitute": "grape juice", "ratio": 1.0, "notes": "Add 1 tbsp vinegar per cup"},
                    {"substitute": "cranberry juice", "ratio": 1.0, "notes": "Add 1 tbsp vinegar per cup"}
                ],
                
                # This will be expanded with more ingredients
            }
    
    def get_substitutions(self, ingredient):
        """
        Get possible substitutions for an ingredient
        
        Args:
            ingredient: The ingredient to find substitutions for
            
        Returns:
            list: List of substitution dictionaries
        """
        ingredient = ingredient.lower()
        
        # Direct lookup in substitutions dictionary
        if ingredient in self.substitutions:
            return self.substitutions[ingredient]
        
        # Check if ingredient is in a category and suggest category alternatives
        category = self.categories.get(ingredient)
        if category:
            # Find other ingredients in the same category
            alternatives = []
            for other_ing in self.category_to_ingredients[category]:
                if other_ing != ingredient:
                    alternatives.append({
                        "substitute": other_ing,
                        "ratio": 1.0,
                        "notes": f"Alternative {category}"
                    })
            
            if alternatives:
                return alternatives
        
        # No substitutions found
        return []
    
    def add_substitution(self, ingredient, substitute, ratio=1.0, unit=None, notes=None):
        """
        Add a new substitution to the knowledge base
        
        Args:
            ingredient: The original ingredient
            substitute: The substitute ingredient
            ratio: The substitution ratio (substitute:original)
            unit: The measurement unit, if applicable
            notes: Additional notes about the substitution
        """
        ingredient = ingredient.lower()
        substitute = substitute.lower()
        
        # Initialize entry if needed
        if ingredient not in self.substitutions:
            self.substitutions[ingredient] = []
        
        # Create the substitution entry
        substitution = {
            "substitute": substitute,
            "ratio": ratio
        }
        
        # Add optional fields if provided
        if unit:
            substitution["unit"] = unit
        if notes:
            substitution["notes"] = notes
        
        # Add to the knowledge base
        self.substitutions[ingredient].append(substitution)
        
        # Automatically update category if needed
        if ingredient in self.categories and substitute not in self.categories:
            category = self.categories[ingredient]
            self.categories[substitute] = category
            self.category_to_ingredients[category].append(substitute)
    
    def add_ingredient_to_category(self, ingredient, category):
        """
        Add an ingredient to a category
        
        Args:
            ingredient: The ingredient to categorize
            category: The category name
        """
        ingredient = ingredient.lower()
        
        # Update the categories dictionary
        self.categories[ingredient] = category
        
        # Update the reverse mapping
        if ingredient not in self.category_to_ingredients[category]:
            self.category_to_ingredients[category].append(ingredient)
    
    def get_category(self, ingredient):
        """
        Get the category of an ingredient
        
        Args:
            ingredient: The ingredient to find the category for
            
        Returns:
            str: Category name or None if not found
        """
        return self.categories.get(ingredient.lower())
    
    def get_ingredients_by_category(self, category):
        """
        Get all ingredients in a category
        
        Args:
            category: The category name
            
        Returns:
            list: List of ingredients in the category
        """
        return self.category_to_ingredients.get(category, [])
    
    def save(self):
        """Save the knowledge base to the filesystem"""
        # Save substitutions
        os.makedirs(os.path.dirname(self.substitutions_path), exist_ok=True)
        with open(self.substitutions_path, 'w') as f:
            json.dump(self.substitutions, f, indent=2)
            
        # Save categories
        with open(self.categories_path, 'w') as f:
            json.dump({
                "categories": self.categories,
                "category_to_ingredients": dict(self.category_to_ingredients)
            }, f, indent=2)
            
        print(f"Saved substitution knowledge base to {self.substitutions_path}")
        print(f"Saved ingredient categories to {self.categories_path}")


# Example usage
if __name__ == "__main__":
    # Create the knowledge base
    kb = SubstitutionKnowledgeBase()
    
    # Print some example substitutions
    test_ingredients = ["butter", "eggs", "milk", "flour", "olive oil", "onion"]
    
    print("Example Substitutions:")
    for ingredient in test_ingredients:
        subs = kb.get_substitutions(ingredient)
        print(f"\n{ingredient.capitalize()}:")
        if subs:
            for sub in subs:
                notes = f" - {sub['notes']}" if 'notes' in sub else ""
                unit = f" {sub['unit']}" if 'unit' in sub else ""
                print(f"  → {sub['ratio']}{unit} {sub['substitute']}{notes}")
        else:
            print("  No substitutions found")
    
    # Save the knowledge base
    kb.save()