import os
import zipfile
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

# Path configurations
BASE_DIR = "/content/drive/MyDrive/food_rescuer"
ARCHIVE_PATH = os.path.join(BASE_DIR, "archive.zip")
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# Ensure directories exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

print(f"Working with archive at: {ARCHIVE_PATH}")

# Extract archive if needed
if not os.path.exists(os.path.join(RAW_DATA_DIR, "RAW_recipes.csv")) and not os.path.exists(os.path.join(RAW_DATA_DIR, "RAW_interactions.csv")):
    print(f"Extracting archive to {RAW_DATA_DIR}...")
    with zipfile.ZipFile(ARCHIVE_PATH, 'r') as zip_ref:
        zip_ref.extractall(RAW_DATA_DIR)
    print("Extraction complete")
else:
    print("Files already extracted")

# List the extracted files
print("\nFiles in raw data directory:")
for file in os.listdir(RAW_DATA_DIR):
    file_path = os.path.join(RAW_DATA_DIR, file)
    if os.path.isfile(file_path):
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        print(f"- {file} ({file_size:.2f} MB)")

# Load the recipes dataset
recipes_file = os.path.join(RAW_DATA_DIR, "RAW_recipes.csv")
if os.path.exists(recipes_file):
    print(f"\nLoading recipes from {recipes_file}...")
    recipes_df = pd.read_csv(recipes_file)
    
    print(f"\nDataset Overview:")
    print(f"- Total recipes: {len(recipes_df)}")
    print(f"- Columns: {', '.join(recipes_df.columns)}")
    
    # Sample a few more rows to better understand quantity format
    print("\nSample Recipe Ingredients:")
    for i in range(min(5, len(recipes_df))):
        sample_recipe = recipes_df.iloc[i]
        ingredients = eval(sample_recipe['ingredients'])
        print(f"Recipe: {sample_recipe['name']}")
        for ing in ingredients[:5]:  # Show first 5 ingredients
            print(f"  - {ing}")
        print()
    
    # Load PP_recipes if available (which might have quantity information)
    pp_recipes_file = os.path.join(RAW_DATA_DIR, "PP_recipes.csv")
    pp_recipes_df = None
    
    if os.path.exists(pp_recipes_file):
        print(f"Loading PP_recipes from {pp_recipes_file} for quantities...")
        try:
            pp_recipes_df = pd.read_csv(pp_recipes_file)
            print(f"Loaded {len(pp_recipes_df)} preprocessed recipes")
        except:
            print("Error loading PP_recipes.csv")
    
    # Process recipes
    max_recipes = 5000  # Limit for prototype
    print(f"\nProcessing up to {max_recipes} recipes...")
    
    # Sample recipes for prototype
    if len(recipes_df) > max_recipes:
        recipes_df = recipes_df.sample(max_recipes, random_state=42)
    
    # Try to add quantities to ingredients
    try:
        # Check if there's a PP_Ingredients.csv file that might have quantity information
        pp_ingredients_file = os.path.join(RAW_DATA_DIR, "PP_Ingredients.csv")
        ingredient_quantities = {}
        
        if os.path.exists(pp_ingredients_file):
            print(f"Loading ingredient quantities from {pp_ingredients_file}...")
            pp_ingredients_df = pd.read_csv(pp_ingredients_file)
            
            # Check the structure
            print(f"PP_Ingredients columns: {', '.join(pp_ingredients_df.columns)}")
            
            # Try to extract quantities
            if 'quantity' in pp_ingredients_df.columns and 'ingredient' in pp_ingredients_df.columns:
                for _, row in pp_ingredients_df.iterrows():
                    ingredient_quantities[row['ingredient']] = row['quantity']
                
                print(f"Loaded quantities for {len(ingredient_quantities)} ingredients")
        
        # If we didn't find quantities, use a lookup dictionary for common ingredients
        if not ingredient_quantities:
            print("Creating default quantity estimates for common ingredients...")
            # Default quantities for common ingredients
            default_quantities = {
                'flour': '2 cups',
                'sugar': '1 cup',
                'salt': '1 tsp',
                'pepper': 'to taste',
                'butter': '1/2 cup',
                'milk': '1 cup',
                'eggs': '2',
                'garlic': '2 cloves',
                'onion': '1 medium',
                'olive oil': '2 tbsp',
                'rice': '1 cup',
                'pasta': '8 oz',
                'water': '2 cups',
                'chicken': '2 breasts',
                'beef': '1 lb',
                'cheese': '1 cup grated',
                'tomatoes': '2 medium',
                'potatoes': '3 medium',
                'carrots': '2 medium',
                'celery': '2 stalks'
            }
            ingredient_quantities = default_quantities
    except Exception as e:
        print(f"Error loading quantities: {e}")
        ingredient_quantities = {}
    
    # Process recipes
    processed_recipes = []
    for _, recipe in recipes_df.iterrows():
        # Parse string representations of lists
        try:
            ingredients = eval(recipe['ingredients'])
            steps = eval(recipe['steps'])
        except:
            # Skip recipes with parsing issues
            continue
        
        # Add estimated quantities to ingredients where possible
        formatted_ingredients = []
        for ingredient in ingredients:
            # Extract the base ingredient name (without quantities or preparations)
            base_ingredient = ingredient.lower().split(',')[0].strip()
            
            # Look for this ingredient in our quantities dictionary
            quantity = ""
            for key, value in ingredient_quantities.items():
                if key in base_ingredient or base_ingredient in key:
                    quantity = value
                    break
            
            # Add the formatted ingredient
            if quantity:
                formatted_ingredients.append({
                    'name': ingredient,
                    'quantity': quantity,
                    'original': ingredient
                })
            else:
                formatted_ingredients.append({
                    'name': ingredient,
                    'quantity': '',
                    'original': ingredient
                })
        
        # Create processed recipe object
        processed_recipe = {
            'id': recipe['id'],
            'name': recipe['name'],
            'ingredients': ingredients,  # Keep original ingredients
            'formatted_ingredients': formatted_ingredients,  # Add formatted version with quantities
            'instructions': steps,
            'minutes': recipe['minutes'],
            'tags': eval(recipe['tags']) if isinstance(recipe['tags'], str) else [],
            'nutrition': eval(recipe['nutrition']) if isinstance(recipe['nutrition'], str) else [],
            'n_steps': recipe['n_steps'],
            'n_ingredients': recipe['n_ingredients']
        }
        
        processed_recipes.append(processed_recipe)
    
    print(f"Processed {len(processed_recipes)} recipes successfully")
    
    # Save processed recipes
    output_path = os.path.join(PROCESSED_DATA_DIR, 'processed_recipes_with_quantities.json')
    with open(output_path, 'w') as f:
        json.dump(processed_recipes, f)
    
    print(f"Saved processed recipes to {output_path}")
    
    # Extract and save unique ingredients
    all_ingredients = set()
    for recipe in processed_recipes:
        all_ingredients.update(recipe['ingredients'])
    
    ingredients_list = list(all_ingredients)
    print(f"Extracted {len(ingredients_list)} unique ingredients")
    
    # Save ingredients list
    ingredients_path = os.path.join(PROCESSED_DATA_DIR, 'ingredients.json')
    with open(ingredients_path, 'w') as f:
        json.dump(ingredients_list, f)
    
    print(f"Saved ingredients list to {ingredients_path}")
    
    print("\nData processing complete!")
else:
    print(f"Error: Recipe file not found at {recipes_file}")
    print("Please check that the archive.zip file was extracted correctly")