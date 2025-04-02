# recipe_data_analyzer.py
# This script analyzes recipe data to understand the ingredient formatting

import os
import json
import re
import sys

def analyze_recipe_data(data_path):
    """Analyze a recipe dataset to understand ingredient format"""
    print(f"Analyzing recipe data from: {data_path}")
    
    try:
        # Load recipe data
        with open(data_path, 'r') as f:
            try:
                recipes = json.load(f)
                print(f"Successfully loaded recipe data: {type(recipes)} with {len(recipes)} items")
            except json.JSONDecodeError:
                # Try to load as lines of JSON objects
                f.seek(0)
                lines = f.readlines()
                recipes = [json.loads(line) for line in lines if line.strip()]
                print(f"Loaded line-delimited JSON with {len(recipes)} recipes")
    except Exception as e:
        print(f"Error loading recipe data: {e}")
        return
    
    # Check data structure
    if isinstance(recipes, dict):
        # Dictionary with recipe_id -> recipe
        recipe_items = list(recipes.items())
        sample_recipes = recipe_items[:5]  # Take first 5 for analysis
    elif isinstance(recipes, list):
        # List of recipes
        sample_recipes = [(i, recipe) for i, recipe in enumerate(recipes[:5])]
    else:
        print(f"Unexpected recipe data structure: {type(recipes)}")
        return
    
    # Analyze sample recipes
    print("\n=== SAMPLE RECIPES ANALYSIS ===")
    
    for i, (recipe_id, recipe) in enumerate(sample_recipes):
        print(f"\nRECIPE {i+1}: {recipe.get('name', 'Unnamed Recipe')} (ID: {recipe_id})")
        
        # Print recipe keys
        print(f"Recipe keys: {', '.join(recipe.keys())}")
        
        # Analyze ingredients
        if 'ingredients' in recipe:
            ingredients = recipe['ingredients']
            print(f"\nIngredients ({len(ingredients)}):")
            
            # Categorize ingredient formats
            format_patterns = {
                "quantity_first": r'^([\d\s./]+\s*[a-zA-Z]*)\s+(.+)$',  # "2 cups flour"
                "quantity_last": r'^(.+),\s*([\d\s./]+\s*[a-zA-Z]*)$',  # "flour, 2 cups"
                "no_quantity": r'^(.+)$'  # "salt to taste"
            }
            
            format_counts = {pattern: 0 for pattern in format_patterns}
            
            for j, ingredient in enumerate(ingredients):
                print(f"  {j+1}. '{ingredient}'")
                
                # Try to match against patterns
                for pattern_name, pattern in format_patterns.items():
                    match = re.match(pattern, ingredient)
                    if match:
                        if pattern_name != "no_quantity" and len(match.groups()) >= 2:
                            if pattern_name == "quantity_first":
                                quantity = match.group(1).strip()
                                name = match.group(2).strip()
                                print(f"     → Pattern: {pattern_name} | Quantity: '{quantity}' | Name: '{name}'")
                            else:
                                name = match.group(1).strip()
                                quantity = match.group(2).strip()
                                print(f"     → Pattern: {pattern_name} | Name: '{name}' | Quantity: '{quantity}'")
                            format_counts[pattern_name] += 1
                            break
                        elif pattern_name == "no_quantity":
                            print(f"     → Pattern: {pattern_name} | Name: '{match.group(1).strip()}'")
                            format_counts[pattern_name] += 1
                            break
            
            print(f"\nIngredient format distribution:")
            for pattern, count in format_counts.items():
                percentage = count / len(ingredients) * 100 if ingredients else 0
                print(f"  {pattern}: {count} ({percentage:.1f}%)")
        else:
            print("No ingredients found in this recipe")
        
        # Check for formatted ingredients
        if 'formatted_ingredients' in recipe:
            print("\nThis recipe already has formatted ingredients:")
            for i, ing in enumerate(recipe['formatted_ingredients']):
                print(f"  {i+1}. {ing}")
    
    # Overall statistics
    print("\n=== OVERALL DATASET STATISTICS ===")
    
    # Count recipes with/without ingredients
    with_ingredients = sum(1 for _, recipe in sample_recipes if 'ingredients' in recipe and recipe['ingredients'])
    print(f"Recipes with ingredients: {with_ingredients}/{len(sample_recipes)}")
    
    # Count recipes with various fields
    fields_count = {}
    for _, recipe in sample_recipes:
        for key in recipe.keys():
            fields_count[key] = fields_count.get(key, 0) + 1
    
    print("\nCommon fields in recipes:")
    for field, count in sorted(fields_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {field}: {count}/{len(sample_recipes)}")
    
    print("\nAnalysis complete")

if __name__ == "__main__":
    # Check for command line argument
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    else:
        # Default path - adjust as needed
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'data', 'processed', 'processed_recipes.json'
        )
    
    analyze_recipe_data(data_path)