# # food_rescuer/models/recipe_retrieval.py
# # Recipe search and ranking system based on available ingredients

# import os
# import json
# import numpy as np
# from collections import defaultdict
# from sentence_transformers import SentenceTransformer

# class RecipeRetriever:
#     """Searches for and ranks recipes based on available ingredients"""
    
#     def __init__(self, data_dir=None, embedding_model='all-MiniLM-L6-v2'):
#         """
#         Initialize the recipe retriever
        
#         Args:
#             data_dir: Directory containing the processed recipe data
#             embedding_model: Name of the sentence transformer model to use
#         """
#         # Set default data directory if not provided
#         if data_dir is None:
#             # Get the directory where this script is located
#             current_dir = os.path.dirname(os.path.abspath(__file__))
#             # Go up one level to the project root
#             project_dir = os.path.dirname(current_dir)
#             data_dir = os.path.join(project_dir, 'data', 'processed')
        
#         self.data_dir = data_dir
#         self.recipes = []
#         self.ingredient_to_recipes = defaultdict(list)
#         self.recipe_embeddings = None
#         self.recipe_ingredients = []
        
#         # Load the sentence transformer model for semantic search
#         try:
#             self.embedding_model = SentenceTransformer(embedding_model)
#             self.use_semantic_search = True
#         except:
#             print("Warning: Sentence transformer model not available, falling back to keyword search")
#             self.use_semantic_search = False
        
#         # Load recipes
#         self._load_recipes()
        
#         # Create ingredient index for faster lookup
#         self._create_ingredient_index()
        
#         # Pre-compute recipe embeddings for semantic search if available
#         if self.use_semantic_search:
#             self._compute_recipe_embeddings()
    
#     def _load_recipes(self):
#         """Load recipes from the processed data directory"""
#         recipes_path = os.path.join(self.data_dir, 'processed_recipes.json')
        
#         if not os.path.exists(recipes_path):
#             print(f"Warning: No processed recipes found at {recipes_path}")
#             return
        
#         with open(recipes_path, 'r') as f:
#             self.recipes = json.load(f)
        
#         print(f"Loaded {len(self.recipes)} recipes")
    
#     def _create_ingredient_index(self):
#         """Create an index mapping ingredients to recipes for faster search"""
#         print("Creating ingredient index...")
        
#         for i, recipe in enumerate(self.recipes):
#             for ingredient in recipe.get('ingredients', []):
#                 ingredient_lower = ingredient.lower()
#                 self.ingredient_to_recipes[ingredient_lower].append(i)
        
#         print(f"Created index with {len(self.ingredient_to_recipes)} ingredients")
    
#     def _compute_recipe_embeddings(self):
#         """Compute ingredient embeddings for all recipes to enable semantic search"""
#         if not self.recipes or not self.use_semantic_search:
#             return
        
#         print("Computing recipe embeddings for semantic search...")
        
#         # Extract ingredient lists as text
#         self.recipe_ingredients = [
#             ' '.join(recipe.get('ingredients', [])) for recipe in self.recipes
#         ]
        
#         # Compute embeddings
#         self.recipe_embeddings = self.embedding_model.encode(self.recipe_ingredients)
        
#         print("Recipe embeddings computed")
    
#     def find_recipes(self, available_ingredients, max_results=10, min_ingredients_matched=1, search_mode='coverage'):
#         """
#         Find recipes that can be made with available ingredients
        
#         Args:
#             available_ingredients: List of ingredients the user has
#             max_results: Maximum number of recipes to return
#             min_ingredients_matched: Minimum number of ingredients that must match
#             search_mode: 'coverage' (% of recipe ingredients available) or 
#                         'count' (total number of matching ingredients) or
#                         'semantic' (semantic similarity to available ingredients)
            
#         Returns:
#             list: List of (recipe, score, matched_ingredients, missing_ingredients) tuples
#         """
#         if not self.recipes:
#             return []
        
#         # Normalize ingredient names
#         available_ingredients = [ing.lower() for ing in available_ingredients]
        
#         if search_mode == 'semantic' and self.use_semantic_search:
#             return self._semantic_search(available_ingredients, max_results)
#         else:
#             return self._keyword_search(available_ingredients, max_results, min_ingredients_matched, search_mode)
    
#     def _keyword_search(self, available_ingredients, max_results, min_ingredients_matched, search_mode):
#         """Find recipes using keyword matching of ingredients"""
#         # Find candidate recipes (any recipe that uses at least one available ingredient)
#         candidate_recipes = set()
#         for ingredient in available_ingredients:
#             candidate_recipes.update(self.ingredient_to_recipes.get(ingredient, []))
        
#         # Score candidate recipes
#         recipe_scores = []
        
#         for recipe_idx in candidate_recipes:
#             recipe = self.recipes[recipe_idx]
#             recipe_ingredients = [ing.lower() for ing in recipe.get('ingredients', [])]
            
#             # Find matching and missing ingredients
#             matched_ingredients = [ing for ing in recipe_ingredients if ing in available_ingredients]
#             missing_ingredients = [ing for ing in recipe_ingredients if ing not in available_ingredients]
            
#             # Skip if too few ingredients match
#             if len(matched_ingredients) < min_ingredients_matched:
#                 continue
            
#             # Calculate score based on search mode
#             if search_mode == 'coverage':
#                 # Percentage of recipe ingredients that are available
#                 score = len(matched_ingredients) / len(recipe_ingredients) if recipe_ingredients else 0
#             elif search_mode == 'count':
#                 # Total number of matching ingredients
#                 score = len(matched_ingredients)
#             else:
#                 # Default to coverage
#                 score = len(matched_ingredients) / len(recipe_ingredients) if recipe_ingredients else 0
            
#             recipe_scores.append((recipe, score, matched_ingredients, missing_ingredients))
        
#         # Sort recipes by score in descending order
#         recipe_scores.sort(key=lambda x: x[1], reverse=True)
        
#         # Return top results
#         return recipe_scores[:max_results]
    
#     def _semantic_search(self, available_ingredients, max_results):
#         """Find recipes using semantic similarity of ingredients"""
#         if not self.recipe_embeddings is not None:
#             print("Semantic search unavailable - fallback to keyword search")
#             return self._keyword_search(available_ingredients, max_results, 1, 'coverage')
        
#         # Create query embedding from available ingredients
#         query = ' '.join(available_ingredients)
#         query_embedding = self.embedding_model.encode(query)
        
#         # Calculate similarity to all recipes
#         similarities = []
        
#         for i, recipe_embedding in enumerate(self.recipe_embeddings):
#             # Calculate cosine similarity
#             similarity = np.dot(query_embedding, recipe_embedding) / (
#                 np.linalg.norm(query_embedding) * np.linalg.norm(recipe_embedding)
#             )
            
#             recipe = self.recipes[i]
#             recipe_ingredients = [ing.lower() for ing in recipe.get('ingredients', [])]
            
#             # Find matching and missing ingredients
#             matched_ingredients = [ing for ing in recipe_ingredients if ing in available_ingredients]
#             missing_ingredients = [ing for ing in recipe_ingredients if ing not in available_ingredients]
            
#             # Create a combined score that considers both semantic similarity and ingredient coverage
#             coverage = len(matched_ingredients) / len(recipe_ingredients) if recipe_ingredients else 0
#             combined_score = 0.7 * similarity + 0.3 * coverage  # Weight semantic similarity higher
            
#             similarities.append((recipe, combined_score, matched_ingredients, missing_ingredients))
        
#         # Sort by similarity score
#         similarities.sort(key=lambda x: x[1], reverse=True)
        
#         # Return top results
#         return similarities[:max_results]

#     # Add this method to your RecipeRetriever class

#     def get_recipe_by_id(self, recipe_id):
#         """
#         Retrieve a specific recipe by ID
        
#         Args:
#             recipe_id: ID of the recipe to retrieve
            
#         Returns:
#             dict: Recipe details or None if not found
#         """
#         # Check if recipe_id is in the recipes dictionary
#         if isinstance(self.recipes, dict) and recipe_id in self.recipes:
#             return self.recipes[recipe_id]
        
#         # If recipes is a list, search by id field
#         if isinstance(self.recipes, list):
#             for recipe in self.recipes:
#                 if recipe.get('id') == recipe_id:
#                     return recipe
        
#         # If we have a more complex structure, iterate through values
#         if isinstance(self.recipes, dict):
#             for recipe in self.recipes.values():
#                 if recipe.get('id') == recipe_id:
#                     return recipe
        
#         return None

#     def get_recipe_by_name(self, recipe_name):
#         """
#         Retrieve a recipe by its name
        
#         Args:
#             recipe_name: Name of the recipe to retrieve
            
#         Returns:
#             dict: Recipe details or None if not found
#         """
#         recipe_name_lower = recipe_name.lower()
        
#         # If recipes is a list, search by name field
#         if isinstance(self.recipes, list):
#             for recipe in self.recipes:
#                 if recipe.get('name', '').lower() == recipe_name_lower:
#                     return recipe
        
#         # If recipes is a dictionary, search values
#         if isinstance(self.recipes, dict):
#             for recipe in self.recipes.values():
#                 if recipe.get('name', '').lower() == recipe_name_lower:
#                     return recipe
        
#         # If no exact match, try partial matching
#         if isinstance(self.recipes, list):
#             matching_recipes = []
#             for recipe in self.recipes:
#                 if recipe_name_lower in recipe.get('name', '').lower():
#                     matching_recipes.append(recipe)
#         else:
#             matching_recipes = []
#             for recipe in self.recipes.values():
#                 if recipe_name_lower in recipe.get('name', '').lower():
#                     matching_recipes.append(recipe)
        
#         # Return the first partial match if any
#         return matching_recipes[0] if matching_recipes else None
        
#     def get_recipe_details(self, recipe_id):
#         """
#         Get detailed information about a specific recipe
        
#         Args:
#             recipe_id: ID of the recipe to retrieve
            
#         Returns:
#             dict: Recipe details or None if not found
#         """
#         # Find recipe by ID
#         for recipe in self.recipes:
#             if recipe.get('id') == recipe_id:
#                 return recipe
        
#         return None
    
#     def find_recipes_by_name(self, query, max_results=10):
#         """
#         Search for recipes by name
        
#         Args:
#             query: Search term to match against recipe names
#             max_results: Maximum number of results to return
            
#         Returns:
#             list: Matching recipes
#         """
#         query = query.lower()
#         matching_recipes = []
        
#         for recipe in self.recipes:
#             name = recipe.get('name', '').lower()
#             if query in name:
#                 matching_recipes.append(recipe)
        
#         # Sort by exact matches first, then alphabetically
#         matching_recipes.sort(key=lambda r: (0 if query == r.get('name', '').lower() else 1, r.get('name', '')))
        
#         return matching_recipes[:max_results]
    
#     def suggest_additional_ingredients(self, recipe, available_ingredients):
#         """
#         Suggest additional ingredients that would enhance a recipe
        
#         Args:
#             recipe: Recipe to enhance
#             available_ingredients: Ingredients the user already has
            
#         Returns:
#             list: Suggested additional ingredients
#         """
#         # Get recipe ingredients
#         recipe_ingredients = set(ing.lower() for ing in recipe.get('ingredients', []))
#         available_ingredients = set(ing.lower() for ing in available_ingredients)
        
#         # Find similar recipes
#         similar_recipes = []
#         for other_recipe in self.recipes:
#             if other_recipe.get('id') == recipe.get('id'):
#                 continue
                
#             other_ingredients = set(ing.lower() for ing in other_recipe.get('ingredients', []))
            
#             # Calculate Jaccard similarity
#             intersection = len(recipe_ingredients.intersection(other_ingredients))
#             union = len(recipe_ingredients.union(other_ingredients))
#             similarity = intersection / union if union > 0 else 0
            
#             if similarity > 0.5:  # Consider recipes with >50% ingredient overlap
#                 similar_recipes.append((other_recipe, similarity))
        
#         # Sort by similarity
#         similar_recipes.sort(key=lambda x: x[1], reverse=True)
        
#         # Identify enhancement ingredients from similar recipes
#         enhancement_ingredients = set()
#         for similar_recipe, _ in similar_recipes[:5]:  # Look at top 5 similar recipes
#             similar_ingredients = set(ing.lower() for ing in similar_recipe.get('ingredients', []))
            
#             # Find ingredients that are in similar recipe but not in original recipe
#             extra_ingredients = similar_ingredients - recipe_ingredients
            
#             # Only suggest ingredients the user already has
#             available_extras = extra_ingredients.intersection(available_ingredients)
#             enhancement_ingredients.update(available_extras)
        
#         return list(enhancement_ingredients)
#     # Add or update this method in your RecipeRetriever class

#     def get_recipe_with_formatted_ingredients(self, recipe_id=None, recipe_name=None, recipe_index=None):
#         """
#         Retrieve a recipe with properly parsed ingredient quantities
        
#         Args:
#             recipe_id: Optional ID to find by ID
#             recipe_name: Optional name to find by name
#             recipe_index: Optional index from suggested recipes
            
#         Returns:
#             dict: Recipe with formatted ingredients or None if not found
#         """
#         recipe = None
        
#         # Try to get by ID first
#         if recipe_id:
#             recipe = self.get_recipe_by_id(recipe_id)
        
#         # Try to get by name
#         if not recipe and recipe_name:
#             recipe = self.get_recipe_by_name(recipe_name)
        
#         # Try to get by index
#         if not recipe and recipe_index is not None:
#             # Handle different data structures
#             if isinstance(self.recipes, list) and 0 <= recipe_index < len(self.recipes):
#                 recipe = self.recipes[recipe_index]
#             elif isinstance(self.recipes, dict) and 0 <= recipe_index < len(self.recipes):
#                 recipe_id = list(self.recipes.keys())[recipe_index]
#                 recipe = self.recipes[recipe_id]
        
#         if not recipe:
#             return None
        
#         # Create a deep copy to avoid modifying original
#         import copy
#         formatted_recipe = copy.deepcopy(recipe)
        
#         # Format ingredients with quantities
#         if 'ingredients' in formatted_recipe:
#             ingredient_list = []
#             for ingredient in formatted_recipe['ingredients']:
#                 # Parse ingredient string into components
#                 import re
                
#                 # Pattern for extracting quantity and ingredient
#                 # This pattern is designed to handle quantities at the beginning of the string
#                 # Example: "60 unsalted butter" or "1⁄4 icing sugar"
#                 quantity_pattern = r'^(\d+(?:\s*\d*\/\d*|\s*\d*⁄\d*)?\s*(?:[a-zA-Z]+)?)\s+(.+)$'
                
#                 match = re.match(quantity_pattern, ingredient)
#                 if match:
#                     quantity = match.group(1).strip()
#                     name = match.group(2).strip()
                    
#                     # Check if quantity is "None" (a common value in the dataset)
#                     if quantity.lower() == 'none':
#                         quantity = ''
#                         name = ingredient
                    
#                     ingredient_list.append({
#                         'name': name,
#                         'quantity': quantity,
#                         'original': ingredient
#                     })
#                 else:
#                     # If the pattern doesn't match, try to find any numbers at the beginning
#                     alternate_match = re.match(r'^(\d+(?:\s*\d*\/\d*)?\s*(?:\d*⁄\d*)?\s*(?:[a-zA-Z]+)?)\s*(.*)$', ingredient)
#                     if alternate_match and alternate_match.group(1).strip() and alternate_match.group(2).strip():
#                         quantity = alternate_match.group(1).strip()
#                         name = alternate_match.group(2).strip()
                        
#                         ingredient_list.append({
#                             'name': name,
#                             'quantity': quantity,
#                             'original': ingredient
#                         })
#                     else:
#                         # Fallback if no pattern matched
#                         ingredient_list.append({
#                             'name': ingredient,
#                             'quantity': '',
#                             'original': ingredient
#                         })
            
#             formatted_recipe['formatted_ingredients'] = ingredient_list
        
#         return formatted_recipe

# # Test the recipe retriever if run directly
# if __name__ == "__main__":
#     retriever = RecipeRetriever()
    
#     # Example search
#     test_ingredients = ["flour", "sugar", "eggs", "butter"]
#     print(f"\nSearching for recipes with ingredients: {', '.join(test_ingredients)}")
    
#     results = retriever.find_recipes(test_ingredients, max_results=5)
    
#     print(f"\nFound {len(results)} matching recipes:")
#     for recipe, score, matched, missing in results:
#         print(f"Recipe: {recipe.get('name')} (Score: {score:.2f})")
#         print(f"  Matched ingredients: {', '.join(matched[:3])}{'...' if len(matched) > 3 else ''}")
#         print(f"  Missing ingredients: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}")

# Modified RecipeRetriever class with improved ingredient matching
# This version will match ingredients regardless of quantities

import os
import json
import re
import numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer

class RecipeRetriever:
    """Searches for and ranks recipes based on available ingredients"""
    
    def __init__(self, data_dir=None, embedding_model='all-MiniLM-L6-v2'):
        """
        Initialize the recipe retriever
        
        Args:
            data_dir: Directory containing the processed recipe data
            embedding_model: Name of the sentence transformer model to use
        """
        # Set default data directory if not provided
        if data_dir is None:
            # Get the directory where this script is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the project root
            project_dir = os.path.dirname(current_dir)
            data_dir = os.path.join(project_dir, 'data', 'processed')
        
        self.data_dir = data_dir
        self.recipes = []
        self.ingredient_to_recipes = defaultdict(list)
        self.recipe_embeddings = None
        self.recipe_ingredients = []
        
        # Store parsed ingredients for each recipe
        self.parsed_recipe_ingredients = []
        
        # Load the sentence transformer model for semantic search
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            self.use_semantic_search = True
        except:
            print("Warning: Sentence transformer model not available, falling back to keyword search")
            self.use_semantic_search = False
        
        # Load recipes
        self._load_recipes()
        
        # Create ingredient index for faster lookup
        self._create_ingredient_index()
        
        # Pre-compute recipe embeddings for semantic search if available
        if self.use_semantic_search:
            self._compute_recipe_embeddings()
    
    def _load_recipes(self):
        """Load recipes from the processed data directory"""
        recipes_path = os.path.join(self.data_dir, 'processed_recipes.json')
        
        if not os.path.exists(recipes_path):
            print(f"Warning: No processed recipes found at {recipes_path}")
            return
        
        with open(recipes_path, 'r') as f:
            self.recipes = json.load(f)
        
        print(f"Loaded {len(self.recipes)} recipes")
    
    def _parse_ingredient(self, ingredient_text):
        """
        Parse an ingredient string to separate name from quantity
        
        Args:
            ingredient_text: Raw ingredient text (e.g., "2 eggs" or "1/2 cup flour")
        
        Returns:
            tuple: (name, quantity) where name is the ingredient name without quantity
        """
        # Pattern to match quantity at the beginning of the string
        # This handles numbers, fractions, and units
        quantity_pattern = r'^(\d+(?:\s*\d*\/\d*|\s*\d*⁄\d*)?\s*(?:[a-zA-Z]+)?)\s+(.+)$'
        
        match = re.match(quantity_pattern, ingredient_text)
        if match:
            quantity = match.group(1).strip()
            name = match.group(2).strip()
            
            # Check if quantity is "None" (a common value in the dataset)
            if quantity.lower() == 'none':
                quantity = ''
                name = ingredient_text
            
            return name, quantity
        
        # If the pattern doesn't match, try another approach
        alternate_match = re.match(r'^(\d+(?:\s*\d*\/\d*)?\s*(?:\d*⁄\d*)?\s*(?:[a-zA-Z]+)?)\s*(.*)$', ingredient_text)
        if alternate_match and alternate_match.group(1).strip() and alternate_match.group(2).strip():
            quantity = alternate_match.group(1).strip()
            name = alternate_match.group(2).strip()
            return name, quantity
        
        # If no quantity found, return the original text as the name
        return ingredient_text, ''
    
    def _create_ingredient_index(self):
        """Create an index mapping ingredients to recipes for faster search"""
        print("Creating ingredient index...")
        
        # Pre-parse all ingredients to extract names without quantities
        self.parsed_recipe_ingredients = []
        
        for i, recipe in enumerate(self.recipes):
            recipe_parsed_ingredients = []
            
            for ingredient in recipe.get('ingredients', []):
                ingredient_name, quantity = self._parse_ingredient(ingredient.lower())
                recipe_parsed_ingredients.append((ingredient_name, quantity))
                
                # Index by ingredient name (without quantity)
                self.ingredient_to_recipes[ingredient_name].append(i)
            
            self.parsed_recipe_ingredients.append(recipe_parsed_ingredients)
        
        print(f"Created index with {len(self.ingredient_to_recipes)} ingredients")
    
    def _compute_recipe_embeddings(self):
        """Compute ingredient embeddings for all recipes to enable semantic search"""
        if not self.recipes or not self.use_semantic_search:
            return
        
        print("Computing recipe embeddings for semantic search...")
        
        # Extract ingredient lists as text (using parsed ingredient names without quantities)
        self.recipe_ingredients = [
            ' '.join([name for name, _ in recipe_ingredients]) 
            for recipe_ingredients in self.parsed_recipe_ingredients
        ]
        
        # Compute embeddings
        self.recipe_embeddings = self.embedding_model.encode(self.recipe_ingredients)
        
        print("Recipe embeddings computed")
    
    def parse_user_ingredients(self, user_ingredients):
        """
        Parse user-provided ingredients to handle cases with and without quantities
        
        Args:
            user_ingredients: List of ingredient strings (may include quantities)
            
        Returns:
            list: List of parsed ingredient names without quantities
        """
        parsed_ingredients = []
        
        for ingredient in user_ingredients:
            # Parse to get just the ingredient name
            name, _ = self._parse_ingredient(ingredient.lower())
            parsed_ingredients.append(name)
        
        return parsed_ingredients
    
    def find_recipes(self, available_ingredients, max_results=10, min_ingredients_matched=1, search_mode='coverage'):
        """
        Find recipes that can be made with available ingredients
        
        Args:
            available_ingredients: List of ingredients the user has
            max_results: Maximum number of recipes to return
            min_ingredients_matched: Minimum number of ingredients that must match
            search_mode: 'coverage' (% of recipe ingredients available) or 
                        'count' (total number of matching ingredients) or
                        'semantic' (semantic similarity to available ingredients)
            
        Returns:
            list: List of (recipe, score, matched_ingredients, missing_ingredients) tuples
        """
        if not self.recipes:
            return []
        
        # Parse user ingredients to extract names without quantities
        parsed_user_ingredients = self.parse_user_ingredients(available_ingredients)
        
        if search_mode == 'semantic' and self.use_semantic_search:
            return self._semantic_search(parsed_user_ingredients, max_results)
        else:
            return self._keyword_search(parsed_user_ingredients, max_results, min_ingredients_matched, search_mode)
    
    def _keyword_search(self, parsed_user_ingredients, max_results, min_ingredients_matched, search_mode):
        """Find recipes using keyword matching of ingredients"""
        # Find candidate recipes (any recipe that uses at least one available ingredient)
        candidate_recipes = set()
        for ingredient in parsed_user_ingredients:
            candidate_recipes.update(self.ingredient_to_recipes.get(ingredient, []))
        
        # Score candidate recipes
        recipe_scores = []
        
        for recipe_idx in candidate_recipes:
            recipe = self.recipes[recipe_idx]
            recipe_parsed_ingredients = self.parsed_recipe_ingredients[recipe_idx]
            
            # Get just the ingredient names (without quantities)
            recipe_ingredient_names = [name for name, _ in recipe_parsed_ingredients]
            
            # Find matching and missing ingredients
            matched_ingredients = []
            missing_ingredients = []
            
            for name in recipe_ingredient_names:
                if any(user_ing in name or name in user_ing for user_ing in parsed_user_ingredients):
                    matched_ingredients.append(name)
                else:
                    missing_ingredients.append(name)
            
            # Skip if too few ingredients match
            if len(matched_ingredients) < min_ingredients_matched:
                continue
            
            # Calculate score based on search mode
            if search_mode == 'coverage':
                # Percentage of recipe ingredients that are available
                score = len(matched_ingredients) / len(recipe_ingredient_names) if recipe_ingredient_names else 0
            elif search_mode == 'count':
                # Total number of matching ingredients
                score = len(matched_ingredients)
            else:
                # Default to coverage
                score = len(matched_ingredients) / len(recipe_ingredient_names) if recipe_ingredient_names else 0
            
            recipe_scores.append((recipe, score, matched_ingredients, missing_ingredients))
        
        # Sort recipes by score in descending order
        recipe_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return recipe_scores[:max_results]
    
    def _semantic_search(self, parsed_user_ingredients, max_results):
        """Find recipes using semantic similarity of ingredients"""
        if not self.recipe_embeddings is not None:
            print("Semantic search unavailable - fallback to keyword search")
            return self._keyword_search(parsed_user_ingredients, max_results, 1, 'coverage')
        
        # Create query embedding from available ingredients
        query = ' '.join(parsed_user_ingredients)
        query_embedding = self.embedding_model.encode(query)
        
        # Calculate similarity to all recipes
        similarities = []
        
        for i, recipe_embedding in enumerate(self.recipe_embeddings):
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, recipe_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(recipe_embedding)
            )
            
            recipe = self.recipes[i]
            recipe_parsed_ingredients = self.parsed_recipe_ingredients[i]
            
            # Get just the ingredient names (without quantities)
            recipe_ingredient_names = [name for name, _ in recipe_parsed_ingredients]
            
            # Find matching and missing ingredients
            matched_ingredients = []
            missing_ingredients = []
            
            for name in recipe_ingredient_names:
                if any(user_ing in name or name in user_ing for user_ing in parsed_user_ingredients):
                    matched_ingredients.append(name)
                else:
                    missing_ingredients.append(name)
            
            # Create a combined score that considers both semantic similarity and ingredient coverage
            coverage = len(matched_ingredients) / len(recipe_ingredient_names) if recipe_ingredient_names else 0
            combined_score = 0.7 * similarity + 0.3 * coverage  # Weight semantic similarity higher
            
            similarities.append((recipe, combined_score, matched_ingredients, missing_ingredients))
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return similarities[:max_results]

    def get_recipe_by_id(self, recipe_id):
        """
        Retrieve a specific recipe by ID
        
        Args:
            recipe_id: ID of the recipe to retrieve
            
        Returns:
            dict: Recipe details or None if not found
        """
        # Check if recipe_id is in the recipes dictionary
        if isinstance(self.recipes, dict) and recipe_id in self.recipes:
            return self.recipes[recipe_id]
        
        # If recipes is a list, search by id field
        if isinstance(self.recipes, list):
            for recipe in self.recipes:
                if recipe.get('id') == recipe_id:
                    return recipe
        
        # If we have a more complex structure, iterate through values
        if isinstance(self.recipes, dict):
            for recipe in self.recipes.values():
                if recipe.get('id') == recipe_id:
                    return recipe
        
        return None

    def get_recipe_by_name(self, recipe_name):
        """
        Retrieve a recipe by its name
        
        Args:
            recipe_name: Name of the recipe to retrieve
            
        Returns:
            dict: Recipe details or None if not found
        """
        recipe_name_lower = recipe_name.lower()
        
        # If recipes is a list, search by name field
        if isinstance(self.recipes, list):
            for recipe in self.recipes:
                if recipe.get('name', '').lower() == recipe_name_lower:
                    return recipe
        
        # If recipes is a dictionary, search values
        if isinstance(self.recipes, dict):
            for recipe in self.recipes.values():
                if recipe.get('name', '').lower() == recipe_name_lower:
                    return recipe
        
        # If no exact match, try partial matching
        if isinstance(self.recipes, list):
            matching_recipes = []
            for recipe in self.recipes:
                if recipe_name_lower in recipe.get('name', '').lower():
                    matching_recipes.append(recipe)
        else:
            matching_recipes = []
            for recipe in self.recipes.values():
                if recipe_name_lower in recipe.get('name', '').lower():
                    matching_recipes.append(recipe)
        
        # Return the first partial match if any
        return matching_recipes[0] if matching_recipes else None
        
    def get_recipe_details(self, recipe_id):
        """
        Get detailed information about a specific recipe
        
        Args:
            recipe_id: ID of the recipe to retrieve
            
        Returns:
            dict: Recipe details or None if not found
        """
        # Find recipe by ID
        for recipe in self.recipes:
            if recipe.get('id') == recipe_id:
                return recipe
        
        return None
    
    def find_recipes_by_name(self, query, max_results=10):
        """
        Search for recipes by name
        
        Args:
            query: Search term to match against recipe names
            max_results: Maximum number of results to return
            
        Returns:
            list: Matching recipes
        """
        query = query.lower()
        matching_recipes = []
        
        for recipe in self.recipes:
            name = recipe.get('name', '').lower()
            if query in name:
                matching_recipes.append(recipe)
        
        # Sort by exact matches first, then alphabetically
        matching_recipes.sort(key=lambda r: (0 if query == r.get('name', '').lower() else 1, r.get('name', '')))
        
        return matching_recipes[:max_results]
    
    def suggest_additional_ingredients(self, recipe, available_ingredients):
        """
        Suggest additional ingredients that would enhance a recipe
        
        Args:
            recipe: Recipe to enhance
            available_ingredients: Ingredients the user already has
            
        Returns:
            list: Suggested additional ingredients
        """
        # Parse user ingredients
        parsed_user_ingredients = self.parse_user_ingredients(available_ingredients)
        
        # Find recipe index
        recipe_id = recipe.get('id')
        recipe_idx = None
        for i, r in enumerate(self.recipes):
            if r.get('id') == recipe_id:
                recipe_idx = i
                break
        
        if recipe_idx is None:
            return []
            
        # Get recipe ingredient names
        recipe_ingredient_names = [name for name, _ in self.parsed_recipe_ingredients[recipe_idx]]
        recipe_ingredients = set(recipe_ingredient_names)
        
        # Find similar recipes
        similar_recipes = []
        for i, other_recipe in enumerate(self.recipes):
            if other_recipe.get('id') == recipe_id:
                continue
                
            other_ingredient_names = [name for name, _ in self.parsed_recipe_ingredients[i]]
            other_ingredients = set(other_ingredient_names)
            
            # Calculate Jaccard similarity
            intersection = len(recipe_ingredients.intersection(other_ingredients))
            union = len(recipe_ingredients.union(other_ingredients))
            similarity = intersection / union if union > 0 else 0
            
            if similarity > 0.5:  # Consider recipes with >50% ingredient overlap
                similar_recipes.append((other_recipe, i, similarity))
        
        # Sort by similarity
        similar_recipes.sort(key=lambda x: x[2], reverse=True)
        
        # Identify enhancement ingredients from similar recipes
        enhancement_ingredients = set()
        for _, similar_idx, _ in similar_recipes[:5]:  # Look at top 5 similar recipes
            similar_ingredient_names = [name for name, _ in self.parsed_recipe_ingredients[similar_idx]]
            similar_ingredients = set(similar_ingredient_names)
            
            # Find ingredients that are in similar recipe but not in original recipe
            extra_ingredients = similar_ingredients - recipe_ingredients
            
            # Check if user has any of these extra ingredients
            for extra in extra_ingredients:
                if any(user_ing in extra or extra in user_ing for user_ing in parsed_user_ingredients):
                    enhancement_ingredients.add(extra)
        
        return list(enhancement_ingredients)

    def get_recipe_with_formatted_ingredients(self, recipe_id=None, recipe_name=None, recipe_index=None):
        """
        Retrieve a recipe with properly parsed ingredient quantities
        
        Args:
            recipe_id: Optional ID to find by ID
            recipe_name: Optional name to find by name
            recipe_index: Optional index from suggested recipes
            
        Returns:
            dict: Recipe with formatted ingredients or None if not found
        """
        recipe = None
        recipe_idx = None
        
        # Try to get by ID first
        if recipe_id:
            for i, r in enumerate(self.recipes):
                if r.get('id') == recipe_id:
                    recipe = r
                    recipe_idx = i
                    break
        
        # Try to get by name
        if not recipe and recipe_name:
            for i, r in enumerate(self.recipes):
                if r.get('name', '').lower() == recipe_name.lower():
                    recipe = r
                    recipe_idx = i
                    break
        
        # Try to get by index
        if not recipe and recipe_index is not None:
            if isinstance(self.recipes, list) and 0 <= recipe_index < len(self.recipes):
                recipe = self.recipes[recipe_index]
                recipe_idx = recipe_index
        
        if not recipe or recipe_idx is None:
            return None
        
        # Create a deep copy to avoid modifying original
        import copy
        formatted_recipe = copy.deepcopy(recipe)
        
        # Get parsed ingredients if available
        if recipe_idx < len(self.parsed_recipe_ingredients):
            parsed_ingredients = self.parsed_recipe_ingredients[recipe_idx]
            
            # Format ingredients with quantities
            ingredient_list = []
            for i, (name, quantity) in enumerate(parsed_ingredients):
                # Get the original ingredient string
                original = recipe.get('ingredients', [])[i] if i < len(recipe.get('ingredients', [])) else f"{quantity} {name}"
                
                ingredient_list.append({
                    'name': name,
                    'quantity': quantity,
                    'original': original
                })
            
            formatted_recipe['formatted_ingredients'] = ingredient_list
        else:
            # Fallback to the original implementation if parsed ingredients not available
            ingredient_list = []
            for ingredient in formatted_recipe.get('ingredients', []):
                name, quantity = self._parse_ingredient(ingredient)
                
                ingredient_list.append({
                    'name': name,
                    'quantity': quantity,
                    'original': ingredient
                })
            
            formatted_recipe['formatted_ingredients'] = ingredient_list
        
        return formatted_recipe

# Test the recipe retriever if run directly
if __name__ == "__main__":
    retriever = RecipeRetriever()
    
    # Example search
    test_ingredients = ["flour", "sugar", "eggs", "butter"]
    print(f"\nSearching for recipes with ingredients: {', '.join(test_ingredients)}")
    
    results = retriever.find_recipes(test_ingredients, max_results=5)
    
    print(f"\nFound {len(results)} matching recipes:")
    for recipe, score, matched, missing in results:
        print(f"Recipe: {recipe.get('name')} (Score: {score:.2f})")
        print(f"  Matched ingredients: {', '.join(matched[:3])}{'...' if len(matched) > 3 else ''}")
        print(f"  Missing ingredients: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}")