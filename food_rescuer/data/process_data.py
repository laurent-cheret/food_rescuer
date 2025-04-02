# food_rescuer/data/process_data.py
# Script to download and process the Food.com dataset

import os
import pandas as pd
import kaggle
import zipfile
import json

# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
DATASET_NAME = 'food-com-recipes-and-user-interactions'
KAGGLE_USERNAME = None  # Fill in your Kaggle username or set via environment variable
KAGGLE_KEY = None  # Fill in your Kaggle API key or set via environment variable

def download_dataset():
    """
    Download the Food.com dataset from Kaggle
    """
    print("Downloading Food.com dataset from Kaggle...")
    
    # Configure Kaggle credentials if provided directly
    if KAGGLE_USERNAME and KAGGLE_KEY:
        os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
        os.environ['KAGGLE_KEY'] = KAGGLE_KEY
    
    # Download the dataset
    try:
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            dataset=f'shuyangli94/{DATASET_NAME}',
            path=RAW_DATA_DIR,
            unzip=True
        )
        print(f"Downloaded dataset to {RAW_DATA_DIR}")
        return True
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        print("\nAlternative: You can manually download the dataset from:")
        print(f"https://www.kaggle.com/datasets/shuyangli94/{DATASET_NAME}")
        print(f"and place it in the {RAW_DATA_DIR} directory")
        return False

def list_available_files():
    """
    List all available files in the raw data directory
    """
    print("\nAvailable files in raw data directory:")
    for file in os.listdir(RAW_DATA_DIR):
        file_path = os.path.join(RAW_DATA_DIR, file)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
            print(f"- {file} ({file_size:.2f} MB)")

def load_and_analyze_recipes():
    """
    Load the recipes dataset and perform basic analysis
    """
    recipes_file = os.path.join(RAW_DATA_DIR, 'RAW_recipes.csv')
    
    if not os.path.exists(recipes_file):
        print(f"Error: Recipe file not found at {recipes_file}")
        return None
    
    print(f"\nLoading recipes from {recipes_file}...")
    recipes_df = pd.read_csv(recipes_file)
    
    print(f"\nDataset Overview:")
    print(f"- Total recipes: {len(recipes_df)}")
    print(f"- Columns: {', '.join(recipes_df.columns)}")
    
    # Display basic statistics
    print("\nBasic Statistics:")
    for col in recipes_df.columns:
        if recipes_df[col].dtype == 'object':
            print(f"- {col}: {recipes_df[col].nunique()} unique values")
        else:
            print(f"- {col}: min={recipes_df[col].min()}, max={recipes_df[col].max()}, mean={recipes_df[col].mean():.2f}")
    
    # Examine the first few recipes
    print("\nSample Recipe:")
    sample_recipe = recipes_df.iloc[0]
    for col, value in sample_recipe.items():
        print(f"- {col}: {value}")
    
    return recipes_df

def process_recipes(recipes_df, max_recipes=5000):
    """
    Process the recipes dataframe into a more usable format
    
    Args:
        recipes_df: DataFrame containing raw recipes
        max_recipes: Maximum number of recipes to process (for prototype)
    """
    if recipes_df is None:
        return
    
    print(f"\nProcessing up to {max_recipes} recipes...")
    
    # Sample recipes for prototype (optional)
    if len(recipes_df) > max_recipes:
        recipes_df = recipes_df.sample(max_recipes, random_state=42)
    
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
        
        # Create processed recipe object
        processed_recipe = {
            'id': recipe['id'],
            'name': recipe['name'],
            'ingredients': ingredients,
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
    output_path = os.path.join(PROCESSED_DATA_DIR, 'processed_recipes.json')
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
    
    return processed_recipes, ingredients_list

def main():
    """
    Main function to download and process the dataset
    """
    # Create directories if they don't exist
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    # Check if we already have the processed data
    processed_file = os.path.join(PROCESSED_DATA_DIR, 'processed_recipes.json')
    if os.path.exists(processed_file):
        print(f"Processed recipes already exist at {processed_file}")
        choice = input("Do you want to reprocess the data? (y/n): ")
        if choice.lower() != 'y':
            print("Using existing processed data.")
            return
    
    # Download dataset if needed
    raw_recipe_file = os.path.join(RAW_DATA_DIR, 'RAW_recipes.csv')
    if not os.path.exists(raw_recipe_file):
        success = download_dataset()
        if not success:
            return
    
    # List available files
    list_available_files()
    
    # Load and analyze recipes
    recipes_df = load_and_analyze_recipes()
    
    # Process recipes
    process_recipes(recipes_df)

if __name__ == "__main__":
    main()