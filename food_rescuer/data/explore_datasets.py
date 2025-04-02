# food_rescuer/data/explore_datasets.py
# Script to explore existing food datasets for ingredient substitution patterns

import os
import json
import pandas as pd
import requests
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

# Path configurations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
DATA_EXPLORATION_DIR = os.path.join(PROCESSED_DATA_DIR, 'exploration')

# Ensure directories exist
os.makedirs(DATA_EXPLORATION_DIR, exist_ok=True)

def explore_food_com_dataset():
    """
    Explore our existing Food.com dataset to mine substitution patterns
    """
    print("Exploring Food.com dataset for substitution patterns...")
    
    # Load processed recipes
    recipes_path = os.path.join(PROCESSED_DATA_DIR, 'processed_recipes.json')
    if not os.path.exists(recipes_path):
        print(f"Error: Processed recipes not found at {recipes_path}")
        return
    
    with open(recipes_path, 'r') as f:
        recipes = json.load(f)
    
    print(f"Loaded {len(recipes)} recipes")
    
    # Group recipes by tag to find similar recipes
    recipes_by_tag = defaultdict(list)
    for recipe in recipes:
        for tag in recipe.get('tags', []):
            recipes_by_tag[tag].append(recipe)
    
    # Find potential substitutions based on similar recipes
    potential_substitutions = defaultdict(lambda: defaultdict(int))
    substitution_confidence = {}
    
    # For each tag with enough recipes
    print("Finding potential substitutions in similar recipes...")
    for tag, tagged_recipes in recipes_by_tag.items():
        if len(tagged_recipes) < 10:
            continue
        
        # For each recipe
        for recipe1 in tagged_recipes[:100]:  # Limit to first 100 for efficiency
            # Extract main dish type from tags if possible
            dish_type = None
            for t in recipe1.get('tags', []):
                if t in ['main-dish', 'dessert', 'breakfast', 'side-dish', 'bread']:
                    dish_type = t
                    break
            
            ingredients1 = set(recipe1.get('ingredients', []))
            
            # For each other recipe with same tag
            for recipe2 in tagged_recipes[:100]:
                if recipe1 == recipe2:
                    continue
                
                ingredients2 = set(recipe2.get('ingredients', []))
                
                # If recipes share most ingredients, differences might be substitutions
                common = ingredients1.intersection(ingredients2)
                if len(common) >= 3:  # They share at least 3 ingredients
                    unique1 = ingredients1 - ingredients2
                    unique2 = ingredients2 - ingredients1
                    
                    # If each has 1-2 unique ingredients, they might be substitutes
                    if 1 <= len(unique1) <= 2 and 1 <= len(unique2) <= 2:
                        for ing1 in unique1:
                            for ing2 in unique2:
                                key = tuple(sorted([ing1, ing2]))
                                potential_substitutions[ing1][ing2] += 1
                                potential_substitutions[ing2][ing1] += 1
                                
                                # Store the dish type for context
                                if dish_type:
                                    if key not in substitution_confidence:
                                        substitution_confidence[key] = {'count': 0, 'contexts': []}
                                    substitution_confidence[key]['count'] += 1
                                    if dish_type not in substitution_confidence[key]['contexts']:
                                        substitution_confidence[key]['contexts'].append(dish_type)
    
    # Convert to list of substitution pairs with counts
    substitution_pairs = []
    for ing1, substitutes in potential_substitutions.items():
        for ing2, count in substitutes.items():
            key = tuple(sorted([ing1, ing2]))
            contexts = substitution_confidence.get(key, {}).get('contexts', [])
            substitution_pairs.append({
                'ingredient1': ing1,
                'ingredient2': ing2,
                'count': count,
                'contexts': contexts
            })
    
    # Sort by count
    substitution_pairs.sort(key=lambda x: x['count'], reverse=True)
    
    # Save the results
    output_path = os.path.join(DATA_EXPLORATION_DIR, 'potential_substitutions.json')
    with open(output_path, 'w') as f:
        json.dump(substitution_pairs[:500], f, indent=2)  # Save top 500
    
    print(f"Saved potential substitutions to {output_path}")
    
    # Print top substitutions
    print("\nTop potential substitutions from Food.com data:")
    for pair in substitution_pairs[:20]:
        contexts = ', '.join(pair['contexts']) if pair['contexts'] else 'various'
        print(f"{pair['ingredient1']} ↔ {pair['ingredient2']}: {pair['count']} co-occurrences (contexts: {contexts})")
    
    return substitution_pairs

def fetch_open_food_facts_sample():
    """
    Fetch a sample of data from Open Food Facts API to explore ingredient relationships
    """
    print("\nFetching sample from Open Food Facts API...")
    
    # API endpoint for a category search (using 'breakfast-cereals' as an example)
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        'action': 'process',
        'tagtype_0': 'categories',
        'tag_contains_0': 'contains',
        'tag_0': 'breakfast-cereals',
        'page_size': 50,
        'json': 1
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'products' in data:
            print(f"Retrieved {len(data['products'])} products")
            
            # Save the sample data
            output_path = os.path.join(DATA_EXPLORATION_DIR, 'open_food_facts_sample.json')
            with open(output_path, 'w') as f:
                json.dump(data['products'], f, indent=2)
            
            # Analyze ingredients
            all_ingredients = []
            for product in data['products']:
                if 'ingredients' in product and isinstance(product['ingredients'], list):
                    for ingredient in product['ingredients']:
                        if 'text' in ingredient:
                            all_ingredients.append(ingredient['text'].lower())
            
            ingredient_counts = pd.Series(all_ingredients).value_counts()
            
            print("\nMost common ingredients in the sample:")
            for ingredient, count in ingredient_counts.head(10).items():
                print(f"- {ingredient}: {count} occurrences")
            
            return data['products']
        else:
            print("Error: No products found in response")
            return None
    
    except Exception as e:
        print(f"Error fetching Open Food Facts data: {e}")
        return None

def check_foodkg_availability():
    """
    Check if FoodKG data is available and provide information on how to access it
    """
    print("\nFood Knowledge Graph (FoodKG) Information:")
    print("FoodKG is a comprehensive knowledge graph containing information about food, recipes,")
    print("ingredients, and their relationships.")
    
    print("\nTo access FoodKG:")
    print("1. Visit the GitHub repository: https://github.com/foodkg/foodkg.github.io")
    print("2. Download the knowledge graph data from the repository")
    print("3. Use the provided tools to query for ingredient relationships")
    
    print("\nFoodKG contains:")
    print("- Recipe data from multiple sources")
    print("- Nutritional information")
    print("- Food-food relationships")
    print("- Food-disease relationships")
    
    print("\nFor this project, you would need to:")
    print("1. Download the FoodKG dataset")
    print("2. Extract ingredient replacement relationships")
    print("3. Convert to the format used by our substitution knowledge base")

def analyze_recipe_ingredient_co_occurrence():
    """
    Analyze ingredient co-occurrences in our dataset to find potential substitutes
    """
    print("\nAnalyzing ingredient co-occurrences for substitution patterns...")
    
    # Load processed recipes
    recipes_path = os.path.join(PROCESSED_DATA_DIR, 'processed_recipes.json')
    if not os.path.exists(recipes_path):
        print(f"Error: Processed recipes not found at {recipes_path}")
        return
    
    with open(recipes_path, 'r') as f:
        recipes = json.load(f)
    
    # Count ingredient occurrences
    ingredient_counts = defaultdict(int)
    for recipe in recipes:
        for ingredient in recipe.get('ingredients', []):
            ingredient_counts[ingredient] += 1
    
    # Filter to common ingredients (occurring in at least 10 recipes)
    common_ingredients = {ing: count for ing, count in ingredient_counts.items() if count >= 10}
    print(f"Found {len(common_ingredients)} common ingredients")
    
    # Create co-occurrence matrix for common ingredients
    ingredients = list(common_ingredients.keys())
    co_occurrence = defaultdict(lambda: defaultdict(int))
    
    # Build co-occurrence counts
    for recipe in recipes:
        recipe_ingredients = [ing for ing in recipe.get('ingredients', []) if ing in common_ingredients]
        for i, ing1 in enumerate(recipe_ingredients):
            for ing2 in recipe_ingredients[i+1:]:
                co_occurrence[ing1][ing2] += 1
                co_occurrence[ing2][ing1] += 1
    
    # Calculate similarity scores
    similarity_scores = defaultdict(dict)
    for ing1 in ingredients:
        ing1_count = ingredient_counts[ing1]
        for ing2 in ingredients:
            if ing1 != ing2:
                ing2_count = ingredient_counts[ing2]
                co_occur_count = co_occurrence[ing1][ing2]
                
                # Calculate Jaccard similarity
                similarity = co_occur_count / (ing1_count + ing2_count - co_occur_count) if co_occur_count > 0 else 0
                
                # Store if similarity is significant
                if similarity > 0.1:  # Threshold for meaningful similarity
                    similarity_scores[ing1][ing2] = similarity
    
    # Extract potential substitution pairs based on high similarity
    substitution_candidates = []
    for ing1, scores in similarity_scores.items():
        for ing2, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if score > 0.2:  # Higher threshold for substitution candidates
                substitution_candidates.append({
                    'ingredient1': ing1,
                    'ingredient2': ing2,
                    'similarity': score,
                    'co_occurrences': co_occurrence[ing1][ing2]
                })
    
    # Sort by similarity score
    substitution_candidates.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Save the results
    output_path = os.path.join(DATA_EXPLORATION_DIR, 'ingredient_similarities.json')
    with open(output_path, 'w') as f:
        json.dump(substitution_candidates[:500], f, indent=2)  # Save top 500
    
    print(f"Saved ingredient similarity data to {output_path}")
    
    # Print top similar pairs
    print("\nTop similar ingredient pairs (potential substitutes):")
    for pair in substitution_candidates[:20]:
        print(f"{pair['ingredient1']} ↔ {pair['ingredient2']}: similarity={pair['similarity']:.3f}, co-occurrences={pair['co_occurrences']}")
    
    return substitution_candidates

def visualize_substitution_network(substitution_pairs, max_pairs=50):
    """
    Create a visualization of potential substitution relationships
    """
    print("\nGenerating substitution network visualization...")
    
    try:
        import networkx as nx
        
        # Create a graph
        G = nx.Graph()
        
        # Add edges for top substitution pairs
        for pair in substitution_pairs[:max_pairs]:
            G.add_edge(
                pair['ingredient1'], 
                pair['ingredient2'], 
                weight=pair['count']
            )
        
        # Calculate node sizes based on degree
        node_sizes = [50 + 10 * G.degree(node) for node in G.nodes()]
        
        # Create the visualization
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(G, seed=42)  # Position the nodes
        
        # Draw the graph
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=1, alpha=0.5)
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        plt.title("Ingredient Substitution Network", fontsize=16)
        plt.axis('off')
        
        # Save the figure
        output_path = os.path.join(DATA_EXPLORATION_DIR, 'substitution_network.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved network visualization to {output_path}")
    
    except ImportError:
        print("Skipping visualization - networkx library not available")

def generate_substitution_database():
    """
    Generate a substitution database based on explored datasets
    """
    print("\nGenerating formal substitution database...")
    
    # Load potential substitutions from Food.com analysis
    pot_subs_path = os.path.join(DATA_EXPLORATION_DIR, 'potential_substitutions.json')
    sim_path = os.path.join(DATA_EXPLORATION_DIR, 'ingredient_similarities.json')
    
    if not os.path.exists(pot_subs_path) or not os.path.exists(sim_path):
        print("Error: Required exploration data not found")
        return
    
    with open(pot_subs_path, 'r') as f:
        potential_substitutions = json.load(f)
    
    with open(sim_path, 'r') as f:
        similarities = json.load(f)
    
    # Combine the two sources of information
    substitution_db = {}
    
    # Process potential substitutions from similar recipes
    for pair in potential_substitutions:
        ing1 = pair['ingredient1']
        ing2 = pair['ingredient2']
        count = pair['count']
        contexts = pair['contexts']
        
        if count < 2:  # Require at least 2 occurrences
            continue
        
        # Add to database
        if ing1 not in substitution_db:
            substitution_db[ing1] = []
        
        substitution_db[ing1].append({
            "substitute": ing2,
            "ratio": 1.0,  # Default ratio
            "confidence": min(1.0, count / 10),  # Scale confidence with count, max 1.0
            "contexts": contexts,
            "notes": f"Found in {count} similar recipes" + (f" for {', '.join(contexts)}" if contexts else "")
        })
    
    # Process similarities
    for pair in similarities:
        ing1 = pair['ingredient1']
        ing2 = pair['ingredient2']
        sim = pair['similarity']
        co_occur = pair['co_occurrences']
        
        if sim < 0.25:  # Require significant similarity
            continue
        
        # Add to database if not already present
        if ing1 not in substitution_db:
            substitution_db[ing1] = []
        
        # Check if already added
        already_added = False
        for sub in substitution_db[ing1]:
            if sub["substitute"] == ing2:
                already_added = True
                # Update with similarity info if not already noted
                if "similarity" not in sub:
                    sub["similarity"] = sim
                break
        
        if not already_added:
            substitution_db[ing1].append({
                "substitute": ing2,
                "ratio": 1.0,  # Default ratio
                "confidence": min(1.0, sim),  # Use similarity as confidence
                "similarity": sim,
                "co_occurrences": co_occur,
                "notes": f"Similarity score: {sim:.2f}, co-occurrences: {co_occur}"
            })
    
    # Save the database
    output_path = os.path.join(PROCESSED_DATA_DIR, 'data_derived_substitutions.json')
    with open(output_path, 'w') as f:
        json.dump(substitution_db, f, indent=2)
    
    print(f"Saved data-derived substitution database to {output_path}")
    print(f"Found substitutions for {len(substitution_db)} ingredients")
    
    # Print some examples
    print("\nExample substitutions from the generated database:")
    common_ingredients = ['butter', 'milk', 'flour', 'eggs', 'olive oil', 'onion', 'sugar']
    
    for ing in common_ingredients:
        if ing in substitution_db:
            print(f"\n{ing.capitalize()} substitutes:")
            for sub in substitution_db[ing][:3]:  # Show up to 3 substitutes
                confidence = f", confidence: {sub['confidence']:.2f}" if 'confidence' in sub else ""
                sim = f", similarity: {sub['similarity']:.2f}" if 'similarity' in sub else ""
                print(f"  → {sub['substitute']}{confidence}{sim}")
                if 'notes' in sub:
                    print(f"     {sub['notes']}")
        else:
            print(f"\n{ing.capitalize()}: No substitutes found")
    
    return substitution_db

def main():
    """Main function to explore all datasets"""
    print("Exploring food datasets for ingredient substitution patterns...")
    
    # Explore our existing Food.com dataset
    substitution_pairs = explore_food_com_dataset()
    
    # Analyze ingredient co-occurrences
    similarity_data = analyze_recipe_ingredient_co_occurrence()
    
    # Visualize substitution network
    if substitution_pairs:
        visualize_substitution_network(substitution_pairs)
    
    # Check FoodKG availability
    check_foodkg_availability()
    
    # Try to fetch Open Food Facts sample
    fetch_open_food_facts_sample()
    
    # Generate substitution database from explored data
    generate_substitution_database()
    
    print("\nData exploration complete!")

if __name__ == "__main__":
    main()