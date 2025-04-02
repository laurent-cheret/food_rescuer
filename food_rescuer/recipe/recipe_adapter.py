# food_rescuer/recipe/recipe_adapter.py
# Handles recipe adaptation based on ingredient substitutions

import os
import json
import re
import sys

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.food_substitutions import SubstitutionKnowledgeBase

class RecipeAdapter:
    """Adapts recipes based on ingredient substitutions"""
    
    def __init__(self, substitution_kb=None):
        """
        Initialize the recipe adapter
        
        Args:
            substitution_kb: SubstitutionKnowledgeBase instance or None to create new one
        """
        # Initialize or use provided substitution knowledge base
        self.substitution_kb = substitution_kb or SubstitutionKnowledgeBase()
    
    def adapt_recipe(self, recipe, missing_ingredients, available_ingredients):
        """
        Adapt a recipe by finding substitutions for missing ingredients
        
        Args:
            recipe: Dictionary containing recipe information
            missing_ingredients: List of ingredients that need substitutions
            available_ingredients: List of ingredients the user has available
            
        Returns:
            dict: Adapted recipe with substitutions
        """
        if not recipe or not missing_ingredients:
            return recipe
        
        # Create a deep copy of the recipe to avoid modifying the original
        adapted_recipe = {
            'id': recipe.get('id'),
            'name': recipe.get('name'),
            'ingredients': recipe.get('ingredients', []).copy(),
            'instructions': recipe.get('instructions', []).copy(),
            'minutes': recipe.get('minutes'),
            'tags': recipe.get('tags', []).copy(),
            'nutrition': recipe.get('nutrition', []).copy(),
            'n_steps': recipe.get('n_steps'),
            'n_ingredients': recipe.get('n_ingredients'),
            'substitutions': []  # New field to track substitutions
        }
        
        # Normalize all strings to lowercase for matching
        missing_ingredients = [ing.lower() for ing in missing_ingredients]
        available_ingredients = [ing.lower() for ing in available_ingredients]
        
        # Process each missing ingredient
        for missing_ingredient in missing_ingredients:
            substitution = self.find_best_substitution(
                missing_ingredient, 
                available_ingredients
            )
            
            if substitution:
                # Add substitution to the tracking list
                adapted_recipe['substitutions'].append({
                    'original': missing_ingredient,
                    'substitute': substitution['substitute'],
                    'ratio': substitution.get('ratio', 1.0),
                    'notes': substitution.get('notes', '')
                })
                
                # Update ingredients list
                self._update_ingredients_list(adapted_recipe, missing_ingredient, substitution)
                
                # Update instructions
                self._update_instructions(adapted_recipe, missing_ingredient, substitution)
        
        return adapted_recipe
    
    def find_best_substitution(self, missing_ingredient, available_ingredients):
        """
        Find the best substitution for a missing ingredient
        
        Args:
            missing_ingredient: Ingredient to substitute
            available_ingredients: List of ingredients the user has available
            
        Returns:
            dict: Substitution information or None if no substitution found
        """
        # Get all possible substitutions for the missing ingredient
        substitutions = self.substitution_kb.get_substitutions(missing_ingredient)
        
        if not substitutions:
            return None
        
        # Filter to substitutions the user has available
        available_substitutions = []
        for sub in substitutions:
            substitute = sub['substitute'].lower()
            if substitute in available_ingredients:
                available_substitutions.append(sub)
        
        if not available_substitutions:
            return None
        
        # Sort by confidence if available, otherwise return the first one
        if 'confidence' in available_substitutions[0]:
            available_substitutions.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return available_substitutions[0]
    
    def _update_ingredients_list(self, recipe, missing_ingredient, substitution):
        """
        Update the ingredients list with the substitution
        
        Args:
            recipe: Recipe to update
            missing_ingredient: Original ingredient
            substitution: Substitution information
        """
        substitute = substitution['substitute']
        ratio = substitution.get('ratio', 1.0)
        
        # Find the missing ingredient in the list
        for i, ingredient in enumerate(recipe['ingredients']):
            if missing_ingredient.lower() in ingredient.lower():
                # Extract quantity if present
                quantity_match = re.match(r'^([\d\s./]+)', ingredient)
                if quantity_match:
                    # There's a numeric quantity
                    quantity_str = quantity_match.group(1).strip()
                    try:
                        # Convert the quantity to a number
                        if '/' in quantity_str:
                            # Handle fractions
                            if ' ' in quantity_str:
                                # Mixed number (e.g., "1 1/2")
                                whole, frac = quantity_str.split(' ', 1)
                                num, denom = frac.split('/')
                                quantity = float(whole) + float(num) / float(denom)
                            else:
                                # Simple fraction (e.g., "1/2")
                                num, denom = quantity_str.split('/')
                                quantity = float(num) / float(denom)
                        else:
                            # Simple number
                            quantity = float(quantity_str)
                        
                        # Adjust the quantity based on substitution ratio
                        adjusted_quantity = quantity * ratio
                        
                        # Format the adjusted quantity
                        if adjusted_quantity.is_integer():
                            adjusted_quantity_str = str(int(adjusted_quantity))
                        else:
                            # Try to convert to a simple fraction for common values
                            if abs(adjusted_quantity - 0.25) < 0.01:
                                adjusted_quantity_str = "1/4"
                            elif abs(adjusted_quantity - 0.33) < 0.01:
                                adjusted_quantity_str = "1/3"
                            elif abs(adjusted_quantity - 0.5) < 0.01:
                                adjusted_quantity_str = "1/2"
                            elif abs(adjusted_quantity - 0.66) < 0.01:
                                adjusted_quantity_str = "2/3"
                            elif abs(adjusted_quantity - 0.75) < 0.01:
                                adjusted_quantity_str = "3/4"
                            else:
                                adjusted_quantity_str = f"{adjusted_quantity:.2f}".rstrip('0').rstrip('.')
                        
                        # Create the new ingredient string
                        rest_of_ingredient = ingredient[len(quantity_str):].replace(missing_ingredient, substitute, 1)
                        new_ingredient = f"{adjusted_quantity_str}{rest_of_ingredient}"
                        
                    except (ValueError, ZeroDivisionError):
                        # If there's an error parsing, just replace the ingredient name
                        new_ingredient = ingredient.replace(missing_ingredient, substitute, 1)
                else:
                    # No quantity found, just replace the ingredient name
                    new_ingredient = ingredient.replace(missing_ingredient, substitute, 1)
                
                # Update the ingredient
                recipe['ingredients'][i] = new_ingredient
                break
    
    def _update_instructions(self, recipe, missing_ingredient, substitution):
        """
        Update the instructions to reflect the substitution
        
        Args:
            recipe: Recipe to update
            missing_ingredient: Original ingredient
            substitution: Substitution information
        """
        substitute = substitution['substitute']
        notes = substitution.get('notes', '')
        
        # Look for the ingredient in each instruction
        for i, instruction in enumerate(recipe['instructions']):
            if missing_ingredient.lower() in instruction.lower():
                # Replace the ingredient name in the instruction
                new_instruction = re.sub(
                    r'\b' + re.escape(missing_ingredient) + r'\b', 
                    substitute, 
                    instruction, 
                    flags=re.IGNORECASE
                )
                
                # Add any special notes if this is the first mention
                if i == 0 and notes:
                    new_instruction += f" (Note: {notes})"
                
                recipe['instructions'][i] = new_instruction
    
    def get_substitution_explanation(self, original, substitute):
        """
        Get a human-readable explanation of a substitution
        
        Args:
            original: Original ingredient
            substitute: Substitute ingredient
            
        Returns:
            str: Explanation of the substitution
        """
        # Get the substitution info
        substitutions = self.substitution_kb.get_substitutions(original)
        
        for sub in substitutions:
            if sub['substitute'].lower() == substitute.lower():
                ratio = sub.get('ratio', 1.0)
                notes = sub.get('notes', '')
                
                # Build the explanation
                explanation = f"You can substitute {substitute} for {original}"
                
                if ratio != 1.0:
                    if ratio > 1.0:
                        explanation += f", using {ratio:.2f}x the amount"
                    else:
                        explanation += f", using {ratio:.2f}x the amount"
                
                if notes:
                    explanation += f". {notes}"
                
                return explanation
        
        # Generic explanation if specific substitution not found
        return f"You can substitute {substitute} for {original}."
    # Add these new methods to your existing RecipeAdapter class

    def find_best_substitution(self, missing_ingredient, available_ingredients):
        """
        Find the best substitution for a missing ingredient with improved matching
        
        Args:
            missing_ingredient: Ingredient to substitute
            available_ingredients: List of ingredients the user has available
            
        Returns:
            dict: Substitution information or None if no substitution found
        """
        # Get all possible substitutions for the missing ingredient
        substitutions = self.substitution_kb.get_substitutions(missing_ingredient)
        
        if not substitutions:
            # Try to find if the ingredient belongs to a category
            category = self.substitution_kb.get_category(missing_ingredient)
            if category:
                # Look for other ingredients in the same category
                category_ingredients = self.substitution_kb.get_ingredients_by_category(category)
                for cat_ing in category_ingredients:
                    if cat_ing.lower() in available_ingredients:
                        return {
                            'substitute': cat_ing,
                            'ratio': 1.0,
                            'notes': f"Alternative {category} ingredient with similar properties"
                        }
            
            # No direct substitutions found
            return None
        
        # Filter to substitutions the user has available
        available_substitutions = []
        for sub in substitutions:
            substitute = sub['substitute'].lower()
            if substitute in available_ingredients:
                available_substitutions.append(sub)
        
        if not available_substitutions:
            # No direct matches, try fuzzy matching against available ingredients
            for sub in substitutions:
                substitute = sub['substitute'].lower()
                # Check for partial matches in user's ingredients
                for available in available_ingredients:
                    # If the substitute is part of an available ingredient or vice versa
                    if substitute in available or available in substitute:
                        return {
                            'substitute': available,
                            'ratio': sub.get('ratio', 1.0),
                            'notes': f"Similar to the suggested substitute ({sub['substitute']})"
                        }
            
            # Still no matches, check if ingredients in the same category are available
            category = self.substitution_kb.get_category(missing_ingredient)
            if category:
                category_ingredients = self.substitution_kb.get_ingredients_by_category(category)
                for cat_ing in category_ingredients:
                    if cat_ing.lower() in available_ingredients:
                        return {
                            'substitute': cat_ing,
                            'ratio': 1.0,
                            'notes': f"Alternative {category} ingredient with similar properties"
                        }
            
            return None
        
        # Sort by confidence if available, otherwise return the first one
        if 'confidence' in available_substitutions[0]:
            available_substitutions.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return available_substitutions[0]

    def suggest_complementary_ingredients(self, recipe, available_ingredients):
        """
        Suggest additional ingredients that would enhance the recipe
        
        Args:
            recipe: Current recipe
            available_ingredients: List of ingredients the user has
            
        Returns:
            list: Suggested complementary ingredients
        """
        # Identify the flavor profile of the recipe
        flavor_profiles = {
            'Italian': ['basil', 'oregano', 'parmesan', 'olive oil', 'tomato', 'garlic'],
            'Mexican': ['cumin', 'cilantro', 'lime', 'chili', 'avocado', 'corn'],
            'Asian': ['soy sauce', 'ginger', 'sesame oil', 'rice vinegar', 'scallion', 'garlic'],
            'Mediterranean': ['olive oil', 'lemon', 'feta', 'yogurt', 'cucumber', 'mint'],
            'Indian': ['cumin', 'coriander', 'turmeric', 'garam masala', 'yogurt', 'ginger']
        }
        
        # Check which profile the recipe most closely matches
        recipe_ingredients = [ing.lower() for ing in recipe.get('ingredients', [])]
        profile_matches = {}
        
        for profile, ingredients in flavor_profiles.items():
            matches = sum(1 for ing in ingredients if any(ing in recipe_ing.lower() for recipe_ing in recipe_ingredients))
            if matches > 0:
                profile_matches[profile] = matches
        
        # Find the best matching profile
        best_profile = max(profile_matches.items(), key=lambda x: x[1])[0] if profile_matches else None
        
        if not best_profile:
            return []
        
        # Suggest ingredients from that profile that the user has but aren't in the recipe
        suggestions = []
        profile_ingredients = flavor_profiles[best_profile]
        
        for available in available_ingredients:
            # Check if the available ingredient is part of the profile but not already in the recipe
            for profile_ing in profile_ingredients:
                if profile_ing in available.lower() and not any(profile_ing in recipe_ing.lower() for recipe_ing in recipe_ingredients):
                    suggestions.append({
                        'ingredient': available,
                        'reason': f"Would complement the {best_profile} flavors in this recipe"
                    })
                    break
        
        return suggestions

    def adjust_recipe_for_dietary_restrictions(self, recipe, restrictions):
        """
        Adjust a recipe to accommodate dietary restrictions
        
        Args:
            recipe: Recipe to adjust
            restrictions: List of dietary restrictions (e.g., 'vegetarian', 'gluten-free')
            
        Returns:
            dict: Adjusted recipe with substitutions for restricted ingredients
        """
        if not recipe or not restrictions:
            return recipe
        
        # Define problematic ingredients for each restriction
        restriction_ingredients = {
            'vegetarian': ['beef', 'chicken', 'pork', 'lamb', 'bacon', 'fish', 'seafood', 'gelatin'],
            'vegan': ['meat', 'beef', 'chicken', 'pork', 'lamb', 'bacon', 'fish', 'seafood', 'milk', 'cream', 
                    'butter', 'cheese', 'yogurt', 'eggs', 'honey', 'gelatin'],
            'gluten-free': ['flour', 'wheat', 'barley', 'rye', 'pasta', 'bread', 'breadcrumbs', 
                          'couscous', 'beer', 'soy sauce'],
            'dairy-free': ['milk', 'cream', 'butter', 'cheese', 'yogurt', 'ice cream', 'sour cream'],
            'nut-free': ['peanut', 'almond', 'cashew', 'pecan', 'walnut', 'pine nut', 'hazelnut',
                        'macadamia', 'brazil nut', 'pistachio']
        }
        
        # Common substitutions for each restriction
        restriction_substitutions = {
            'vegetarian': {
                'beef': 'vegetable broth',
                'chicken': 'tofu',
                'pork': 'tempeh',
                'bacon': 'smoked paprika',
                'fish': 'tofu',
                'gelatin': 'agar-agar'
            },
            'vegan': {
                'milk': 'almond milk',
                'cream': 'coconut cream',
                'butter': 'olive oil',
                'cheese': 'nutritional yeast',
                'yogurt': 'coconut yogurt',
                'eggs': 'flax eggs',
                'honey': 'maple syrup',
                'beef': 'lentils',
                'chicken': 'tofu',
                'pork': 'jackfruit',
                'bacon': 'smoked paprika',
                'fish': 'tofu',
                'gelatin': 'agar-agar'
            },
            'gluten-free': {
                'flour': 'gluten-free flour blend',
                'bread': 'gluten-free bread',
                'pasta': 'gluten-free pasta',
                'breadcrumbs': 'gluten-free breadcrumbs',
                'soy sauce': 'tamari'
            },
            'dairy-free': {
                'milk': 'almond milk',
                'cream': 'coconut cream',
                'butter': 'olive oil',
                'cheese': 'nutritional yeast',
                'yogurt': 'coconut yogurt',
                'sour cream': 'coconut cream with lemon juice'
            },
            'nut-free': {
                'peanut butter': 'sunflower seed butter',
                'almond milk': 'oat milk',
                'cashew cream': 'coconut cream'
            }
        }
        
        # Create a copy of the recipe to modify
        adjusted_recipe = dict(recipe)
        adjusted_recipe['ingredients'] = recipe.get('ingredients', []).copy()
        adjusted_recipe['instructions'] = recipe.get('instructions', []).copy()
        
        if 'substitutions' not in adjusted_recipe:
            adjusted_recipe['substitutions'] = []
        
        # For each restriction, find problematic ingredients and substitute them
        for restriction in restrictions:
            if restriction.lower() not in restriction_ingredients:
                continue
            
            problem_ingredients = restriction_ingredients[restriction.lower()]
            substitutions = restriction_substitutions.get(restriction.lower(), {})
            
            # Check each ingredient in the recipe
            recipe_ingredients = adjusted_recipe['ingredients'].copy()
            for i, ingredient_str in enumerate(recipe_ingredients):
                ingredient_lower = ingredient_str.lower()
                
                # Find any problematic ingredients
                for problem in problem_ingredients:
                    if problem in ingredient_lower:
                        # Get substitution if available
                        substitute = None
                        for key, value in substitutions.items():
                            if key in ingredient_lower:
                                substitute = value
                                break
                        
                        if substitute:
                            # Replace the ingredient
                            new_ingredient = ingredient_str.replace(problem, substitute)
                            adjusted_recipe['ingredients'][i] = new_ingredient
                            
                            # Add to substitutions list
                            adjusted_recipe['substitutions'].append({
                                'original': problem,
                                'substitute': substitute,
                                'ratio': 1.0,
                                'notes': f"For {restriction} diet"
                            })
                            
                            # Update instructions if needed
                            for j, instruction in enumerate(adjusted_recipe['instructions']):
                                if problem in instruction.lower():
                                    adjusted_recipe['instructions'][j] = instruction.replace(problem, substitute)
        
        # Add a note about dietary modifications
        if adjusted_recipe['substitutions']:
            adjusted_recipe['dietary_modifications'] = restrictions
            
        return adjusted_recipe

# Test the recipe adapter if run directly
if __name__ == "__main__":
    adapter = RecipeAdapter()
    
    # Example recipe
    test_recipe = {
        'name': 'Simple Cake',
        'ingredients': [
            '2 cups flour',
            '1 cup sugar',
            '1/2 cup butter',
            '2 eggs',
            '1 cup milk',
            '1 tsp baking powder',
            '1 tsp vanilla extract'
        ],
        'instructions': [
            'Preheat oven to 350°F (175°C)',
            'Cream together butter and sugar',
            'Beat in eggs one at a time',
            'Add vanilla extract',
            'Mix in flour and baking powder',
            'Gradually add milk',
            'Pour batter into pan and bake for 30 minutes'
        ]
    }
    
    # Missing and available ingredients
    missing = ['butter', 'milk']
    available = ['olive oil', 'water', 'yogurt', 'flour', 'sugar', 'eggs', 'baking powder', 'vanilla extract']
    
    # Adapt the recipe
    adapted_recipe = adapter.adapt_recipe(test_recipe, missing, available)
    
    # Print original and adapted recipe
    print("Original Recipe:")
    print(f"Name: {test_recipe['name']}")
    print("Ingredients:")
    for ing in test_recipe['ingredients']:
        print(f"  - {ing}")
    
    print("\nAdapted Recipe:")
    print(f"Name: {adapted_recipe['name']}")
    print("Ingredients:")
    for ing in adapted_recipe['ingredients']:
        print(f"  - {ing}")
    
    print("\nSubstitutions:")
    for sub in adapted_recipe.get('substitutions', []):
        explanation = adapter.get_substitution_explanation(sub['original'], sub['substitute'])
        print(f"  - {explanation}")
    
    print("\nInstructions:")
    for i, instruction in enumerate(adapted_recipe['instructions']):
        print(f"{i+1}. {instruction}")