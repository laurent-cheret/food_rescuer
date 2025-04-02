# food_rescuer/data/analyze_data.py
# Script to analyze the processed Food.com dataset

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter

# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

def load_processed_data():
    """
    Load the processed recipes and ingredients
    """
    recipes_path = os.path.join(PROCESSED_DATA_DIR, 'processed_recipes.json')
    ingredients_path = os.path.join(PROCESSED_DATA_DIR, 'ingredients.json')
    
    if not os.path.exists(recipes_path) or not os.path.exists(ingredients_path):
        print("Processed data not found. Please run process_data.py first.")
        return None, None
    
    with open(recipes_path, 'r') as f:
        recipes = json.load(f)
    
    with open(ingredients_path, 'r') as f:
        ingredients = json.load(f)
    
    print(f"Loaded {len(recipes)} processed recipes and {len(ingredients)} unique ingredients")
    return recipes, ingredients

def analyze_recipe_complexity(recipes):
    """
    Analyze the complexity of recipes (number of ingredients, steps)
    """
    if not recipes:
        return
    
    n_ingredients = [r['n_ingredients'] for r in recipes]
    n_steps = [r['n_steps'] for r in recipes]
    
    print("\nRecipe Complexity Analysis:")
    print(f"- Average ingredients per recipe: {np.mean(n_ingredients):.2f}")
    print(f"- Average steps per recipe: {np.mean(n_steps):.2f}")
    print(f"- Max ingredients in a recipe: {max(n_ingredients)}")
    print(f"- Max steps in a recipe: {max(n_steps)}")
    
    # Create ingredients histogram
    plt.figure(figsize=(10, 6))
    plt.hist(n_ingredients, bins=20, alpha=0.7)
    plt.title('Distribution of Number of Ingredients per Recipe')
    plt.xlabel('Number of Ingredients')
    plt.ylabel('Number of Recipes')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(PROCESSED_DATA_DIR, 'ingredients_histogram.png')
    plt.savefig(output_path)
    print(f"Saved ingredients histogram to {output_path}")
    plt.close()

def analyze_common_ingredients(recipes):
    """
    Analyze the most common ingredients
    """
    if not recipes:
        return
    
    # Count ingredient occurrences
    all_ingredients = []
    for recipe in recipes:
        all_ingredients.extend(recipe['ingredients'])
    
    ingredient_counts = Counter(all_ingredients)
    top_ingredients = ingredient_counts.most_common(20)
    
    print("\nTop 20 Most Common Ingredients:")
    for ingredient, count in top_ingredients:
        print(f"- {ingredient}: {count} recipes")
    
    # Plot top ingredients
    plt.figure(figsize=(12, 8))
    ingredients, counts = zip(*top_ingredients)
    plt.barh(ingredients, counts)
    plt.xlabel('Number of Recipes')
    plt.title('Top 20 Most Common Ingredients')
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(PROCESSED_DATA_DIR, 'top_ingredients.png')
    plt.savefig(output_path)
    print(f"Saved top ingredients chart to {output_path}")
    plt.close()
    
    return ingredient_counts

def analyze_cooking_times(recipes):
    """
    Analyze cooking times
    """
    if not recipes:
        return
    
    cooking_times = [r['minutes'] for r in recipes if r['minutes'] < 300]  # Filter out extreme values
    
    print("\nCooking Time Analysis:")
    print(f"- Average cooking time: {np.mean(cooking_times):.2f} minutes")
    print(f"- Median cooking time: {np.median(cooking_times):.2f} minutes")
    
    # Plot cooking time distribution
    plt.figure(figsize=(10, 6))
    plt.hist(cooking_times, bins=30, alpha=0.7)
    plt.title('Distribution of Cooking Times')
    plt.xlabel('Cooking Time (minutes)')
    plt.ylabel('Number of Recipes')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(PROCESSED_DATA_DIR, 'cooking_times.png')
    plt.savefig(output_path)
    print(f"Saved cooking times histogram to {output_path}")
    plt.close()

def analyze_recipe_tags(recipes):
    """
    Analyze recipe tags
    """
    if not recipes:
        return
    
    # Count tag occurrences
    all_tags = []
    for recipe in recipes:
        all_tags.extend(recipe['tags'])
    
    tag_counts = Counter(all_tags)
    top_tags = tag_counts.most_common(20)
    
    print("\nTop 20 Most Common Tags:")
    for tag, count in top_tags:
        print(f"- {tag}: {count} recipes")
    
    # Plot top tags
    plt.figure(figsize=(12, 8))
    tags, counts = zip(*top_tags)
    plt.barh(tags, counts)
    plt.xlabel('Number of Recipes')
    plt.title('Top 20 Most Common Tags')
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(PROCESSED_DATA_DIR, 'top_tags.png')
    plt.savefig(output_path)
    print(f"Saved top tags chart to {output_path}")
    plt.close()

def find_ingredient_co_occurrences(recipes, ingredient_counts, min_count=100):
    """
    Find ingredients that commonly occur together
    """
    if not recipes:
        return
    
    # Filter to common ingredients only
    common_ingredients = {ing for ing, count in ingredient_counts.items() if count >= min_count}
    
    print(f"\nAnalyzing co-occurrences among {len(common_ingredients)} common ingredients...")
    
    # Create co-occurrence matrix
    co_occurrence = {}
    for ing in common_ingredients:
        co_occurrence[ing] = Counter()
    
    # Count co-occurrences
    for recipe in recipes:
        recipe_ingredients = set(recipe['ingredients']) & common_ingredients
        for ing1 in recipe_ingredients:
            for ing2 in recipe_ingredients:
                if ing1 != ing2:
                    co_occurrence[ing1][ing2] += 1
    
    # Find top co-occurring pairs
    top_pairs = []
    for ing1, counter in co_occurrence.items():
        for ing2, count in counter.most_common(5):
            # Only include each pair once
            if (ing2, ing1, count) not in top_pairs:
                top_pairs.append((ing1, ing2, count))
    
    # Sort by count
    top_pairs.sort(key=lambda x: x[2], reverse=True)
    
    # Print top 20 co-occurring pairs
    print("\nTop 20 Ingredient Co-occurrences:")
    for ing1, ing2, count in top_pairs[:20]:
        print(f"- {ing1} + {ing2}: {count} recipes")
    
    # Save co-occurrence data
    co_occurrence_data = {ing: dict(counter) for ing, counter in co_occurrence.items()}
    output_path = os.path.join(PROCESSED_DATA_DIR, 'ingredient_co_occurrences.json')
    with open(output_path, 'w') as f:
        json.dump(co_occurrence_data, f)
    
    print(f"Saved ingredient co-occurrences to {output_path}")

def main():
    """
    Main function to analyze the processed dataset
    """
    print("Analyzing Food.com dataset...")
    
    # Load processed data
    recipes, ingredients = load_processed_data()
    if not recipes:
        return
    
    # Analyze recipe complexity
    analyze_recipe_complexity(recipes)
    
    # Analyze common ingredients
    ingredient_counts = analyze_common_ingredients(recipes)
    
    # Analyze cooking times
    analyze_cooking_times(recipes)
    
    # Analyze recipe tags
    analyze_recipe_tags(recipes)
    
    # Find ingredient co-occurrences
    find_ingredient_co_occurrences(recipes, ingredient_counts)
    
    print("\nAnalysis completed successfully!")

if __name__ == "__main__":
    main()