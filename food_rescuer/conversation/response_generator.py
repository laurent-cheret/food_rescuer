# food_rescuer/conversation/response_generator.py
# Generates natural language responses based on intent and context

import random
import re

# This would go in your conversation/response_generator.py file

import random

# food_rescuer/conversation/response_generator.py
# Generate natural language responses for different conversation scenarios

import random

def generate_response(response_type, data=None):
    """
    Generate a natural language response based on the type and data
    
    Args:
        response_type: Type of response to generate
        data: Data to include in the response
        
    Returns:
        str: Generated response
    """
    data = data or {}
    
    # Define response templates for each response type
    templates = {
        'greeting': [
            "Hello! I'm Food Rescuer, your cooking assistant. What ingredients do you have today?",
            "Hi there! Ready to create something delicious? Tell me what ingredients you have.",
            "Welcome to Food Rescuer! I can help you find recipes with ingredients you already have."
        ],
        
        'ask_for_ingredients': [
            "What ingredients do you have available?",
            "Tell me what ingredients you have, and I'll find something delicious to make.",
            "What's in your kitchen today? I can suggest recipes based on what you have."
        ],
        
        'ingredients_added': [
            "Great! I've added {ingredients_list} to your available ingredients. What else do you have?",
            "Got it, {ingredients_list} added to your ingredients. Anything else in your kitchen?",
            "I've noted that you have {ingredients_list}. Any other ingredients to add?"
        ],
        
        'ingredients_added_suggest_search': [
            "I've added {ingredients_list} to your available ingredients. Would you like to find recipes you can make?",
            "Great! You now have {total_count} ingredients: {ingredients_list}. Shall I suggest some recipes?",
            "I've updated your ingredient list with {ingredients_list}. Ready to see what you can cook?"
        ],
        
        'recipe_found': [
            "I found a great recipe for you: {recipe_name}! You have {match_percentage}% of the required ingredients.",
            "How about making {recipe_name}? You already have {match_count} of the {total_ingredients} ingredients needed.",
            "Based on your ingredients, I recommend {recipe_name}. You're just missing {missing_count} ingredients: {missing_list}."
        ],
        
        'no_recipes_found': [
            "I couldn't find any recipes that match your ingredients exactly. Try adding a few more ingredients, or I can suggest some recipes that require just a few additional items.",
            "You don't have enough ingredients for complete recipes in my collection. Would you like to see recipes that need just 1-2 more ingredients?",
            "I don't have recipes that perfectly match your current ingredients. Would you like to add more ingredients or see recipes that require a few additional items?"
        ],
        
        'recipe_details': [
            "Here's the full recipe for {recipe_name}:\n\n{recipe_details}",
            "Here's how to make {recipe_name}:\n\n{recipe_details}",
            "{recipe_name} Recipe:\n\n{recipe_details}"
        ],
        
        'no_current_recipe': [
            "We haven't selected a recipe yet. Would you like to search for recipes with your current ingredients?",
            "I don't have a recipe selected. Tell me what ingredients you have, and I'll find a recipe for you.",
            "No recipe is currently selected. Let's find one based on your ingredients!"
        ],
        
        'ask_what_ingredient_missing': [
            "Which ingredient are you missing?",
            "What ingredient do you need a substitute for?",
            "Tell me which ingredient you don't have, and I'll suggest alternatives."
        ],
        
        'substitution_found': [
            "Instead of {ingredient}, you can use {substitute}. {notes}",
            "No {ingredient}? No problem! Use {substitute} instead. {notes}",
            "You can substitute {ingredient} with {substitute}. {notes}"
        ],
        
        'substitution_suggested': [
            "For {ingredient}, you could use {substitutions_list}, but it looks like you don't have those either. Would you like to see a different recipe?",
            "I'd normally suggest {substitutions_list} as alternatives for {ingredient}, but you don't have those. Want to try another recipe?",
            "You could substitute {ingredient} with {substitutions_list}, but you don't have those ingredients. Should we look for another recipe?"
        ],
        
        'no_substitution_found': [
            "I don't know any substitutes for {ingredient}. This ingredient might be essential for the recipe. Would you like to try a different recipe?",
            "Unfortunately, I don't have alternatives for {ingredient}. Would you like to see a different recipe?",
            "I can't suggest a substitute for {ingredient}. Would you like to find a recipe that doesn't need it?"
        ],
        
        'next_step': [
            "Step {step_number} of {total_steps}: {current_step}",
            "Next step ({step_number}/{total_steps}): {current_step}",
            "Here's what to do next (Step {step_number}/{total_steps}): {current_step}"
        ],
        
        'previous_step': [
            "Going back to step {step_number} of {total_steps}: {current_step}",
            "Previous step ({step_number}/{total_steps}): {current_step}",
            "Let's go back to step {step_number}: {current_step}"
        ],
        
        'recipe_completed': [
            "That's the last step! Your {recipe_name} should be ready to enjoy. How did it turn out?",
            "You've completed all the steps for {recipe_name}! I hope it's delicious!",
            "Congratulations! You've finished making {recipe_name}. Enjoy your meal!"
        ],
        
        'ingredient_now_available': [
            "Great! I've updated your ingredients to include {ingredient}.",
            "Perfect! I've added {ingredient} to your available ingredients.",
            "Excellent! I'll note that you do have {ingredient} after all."
        ],
        
        'ingredient_confirmed': [
            "Great! I've noted that you have {ingredient}.",
            "Perfect! I've added {ingredient} to your available ingredients.",
            "Got it, you have {ingredient}."
        ],
        
        'ingredient_quantity': [
            "For this recipe, you need {quantity}.",
            "The recipe calls for {quantity}.",
            "You'll need {quantity} for this recipe."
        ],
        
        'ingredient_not_in_recipe': [
            "{ingredient} isn't needed for {recipe_name}.",
            "This recipe doesn't call for {ingredient}.",
            "{recipe_name} doesn't use {ingredient}."
        ],
        
        'dietary_restriction_noted': [
            "I've noted your {restrictions} dietary preference. I'll keep this in mind when suggesting recipes.",
            "Got it, you prefer {restrictions} food. I'll suggest appropriate recipes.",
            "I'll remember your {restrictions} preference for future recipe suggestions."
        ],
        
        'help': [
            "I can help you find and cook recipes based on ingredients you have. Try saying 'I have eggs and flour' or 'What can I make with chicken?'. Once we're cooking, you can ask for the next step or request substitutions for ingredients you don't have.",
            "Food Rescuer helps you cook with what you have. Tell me your ingredients, and I'll suggest recipes. During cooking, I can guide you through each step and suggest substitutions for missing ingredients.",
            "I'm your cooking assistant! Tell me what ingredients you have, and I'll find recipes. If you're missing something, I can suggest substitutes. I can also guide you through recipes step by step."
        ],
        
        'congratulate_completion': [
            "Congratulations on completing {recipe_name}! I hope it turned out delicious!",
            "Well done! You've finished making {recipe_name}. Enjoy your meal!",
            "Great job finishing {recipe_name}! How did it turn out?"
        ],
        
        'thank_for_feedback': [
            "Thank you for your feedback on {recipe_name}! I'm glad I could help.",
            "I appreciate your feedback on {recipe_name}! Is there anything else you'd like to cook?",
            "Thanks for letting me know how {recipe_name} turned out! Would you like to try another recipe?"
        ],
        
        'proceed_with_recipe': [
            "Great! Let's proceed with making {recipe_name} even without that ingredient.",
            "Perfect! Let's continue with {recipe_name}. We'll work around the missing ingredient.",
            "Excellent! We'll make {recipe_name} with what you have. Ready for the first step?"
        ],
        
        'suggest_different_recipe': [
            "No problem. Let me find a different recipe that better matches your available ingredients.",
            "I understand. Let's look for another recipe that uses what you have.",
            "Sure thing. I'll search for alternative recipes based on your ingredients."
        ],
        
        'acknowledged': [
            "Great! Let's continue.",
            "Perfect! Let's proceed.",
            "Excellent! Moving forward."
        ],
        
        'acknowledged_negative': [
            "No problem. What would you like to do instead?",
            "That's fine. What would you prefer to do?",
            "I understand. How else can I help you?"
        ],
        
        'discuss_ingredient': [
            "{ingredient} is a versatile ingredient! You now have {total_ingredients} ingredients. Would you like to see recipes using {ingredient}?",
            "I've added {ingredient} to your ingredients. Want to find recipes that use it?",
            "{ingredient} is great! With your {total_ingredients} ingredients, I can suggest some delicious recipes. Would you like to see them?"
        ],
        
        'unknown_initial': [
            "I'm not sure I understand. I can help you find recipes based on ingredients you have. Try saying 'I have eggs and flour' or 'What can I make with chicken?'",
            "I didn't quite catch that. Tell me what ingredients you have, and I'll suggest recipes you can make.",
            "I'm not sure what you're asking. I can help you find and cook recipes with ingredients you already have. What ingredients do you have?"
        ],
        
        'unknown_with_ingredients': [
            "I'm not sure what you're asking. You've told me about {num_ingredients} ingredients. Would you like to find recipes using them?",
            "I didn't quite understand. So far, you've mentioned {num_ingredients} ingredients. Shall I suggest recipes you can make?",
            "I'm not sure how to help with that. Based on your {num_ingredients} ingredients, I can suggest recipes if you'd like."
        ],
        
        'unknown_with_recipe': [
            "I'm not sure what you're asking. We're currently working on {recipe_name}. Would you like to see the next step, get recipe details, or find a substitution?",
            "I didn't quite catch that. We're making {recipe_name}. Do you want to continue with the recipe, find substitutions, or try something else?",
            "I'm not sure how to help with that. We're in the middle of making {recipe_name}. Do you want to continue, or would you like to do something else?"
        ],
        
        'recipe_enhancement': [
            "To enhance your {recipe_name}, I recommend adding {suggestions_list}. These ingredients would complement the existing flavors really well.",
            "Want to make your {recipe_name} even better? Try adding {suggestions_list} to enhance the flavor profile.",
            "For an upgraded version of {recipe_name}, consider adding {suggestions_list}. These ingredients will take it to the next level!"
        ],
        
        'no_enhancement_needed': [
            "Your {recipe_name} recipe looks great as is! The ingredients you have create a well-balanced dish.",
            "I don't have any specific enhancement suggestions for {recipe_name}. The recipe is already well balanced with the ingredients you have.",
            "The {recipe_name} recipe has a good combination of flavors already. It should turn out delicious as is!"
        ],
        
        'recipe_adapted_for_diet': [
            "I've adapted the {recipe_name} recipe to be {restrictions} friendly! I've substituted {substitutions_list} to accommodate your dietary preferences.",
            "Good news! I've modified the {recipe_name} recipe to suit your {restrictions} needs. I've replaced {substitutions_list}.",
            "Your {recipe_name} recipe is now {restrictions} compatible. I've made these substitutions: {substitutions_list}."
        ],
        
        'dietary_restriction_unclear': [
            "I'm not sure I understood your dietary restriction. Could you clarify? For example, are you vegetarian, vegan, gluten-free, or have other dietary needs?",
            "I'd like to help with your dietary needs, but I didn't catch what they are. Could you specify your dietary restrictions?",
            "What specific dietary restrictions should I keep in mind when suggesting recipes for you?"
        ],
        
        'first_step': [
            "Let's start with the first step for {recipe_name}: {current_step}",
            "Here's how to begin making {recipe_name}: {current_step}",
            "Let's get cooking! Step 1 for {recipe_name}: {current_step}"
        ],
        
        'general_thanks': [
            "You're welcome! I'm happy to help with your cooking.",
            "My pleasure! Let me know if you need help with anything else.",
            "Glad I could assist. Would you like to try another recipe?"
        ],
        
        'no_search': [
            "No problem. Let me know when you want to search for recipes or if you'd like to add more ingredients.",
            "That's fine. What would you like to do instead?",
            "Sure thing. Just let me know when you're ready to find recipes using your ingredients."
        ],

        'multiple_recipes_found': [
            "Here are some recipes you can make with your ingredients:\n\n{recipe_list}\n\nWhich recipe would you like to see? You can say the number or name.",
            "I found {recipe_count} recipes that match your ingredients:\n\n{recipe_list}\n\nWhich one would you like to try? Just say the number or name.",
            "Based on your available ingredients, you could make:\n\n{recipe_list}\n\nWhich recipe interests you? Tell me the number or name."
        ],

        'recipe_selected': [
            "Great choice! {recipe_name} uses {match_percentage}% of your available ingredients. You have {matched_count} of the required ingredients and are missing {missing_count}: {missing_list}. Would you like to see the full recipe?",
            "You selected {recipe_name}. You already have {matched_count} ingredients for this recipe and are missing {missing_count}: {missing_list}. Ready to see the full recipe?",
            "{recipe_name} is a good choice! You have {match_percentage}% of the ingredients needed. Missing: {missing_list}. Would you like to see the complete recipe?"
        ],

        'invalid_recipe_selection': [
            "I couldn't find that recipe in the list. Please select a number between 1 and {total_recipes}, or say the name of one of the recipes I suggested.",
            "That selection isn't valid. Please choose a recipe number from 1 to {total_recipes}, or specify the name of one of the suggested recipes.",
            "I don't see that recipe in the options. Choose a number from 1-{total_recipes} or tell me the name of the recipe you want to see."
        ],

        'substitution_options': [
            "For {ingredient}, you could use: {substitutions_list}. Would you like to use one of these substitutes?",
            "No {ingredient}? You can substitute it with: {substitutions_list}. Which would you prefer to use?",
            "Instead of {ingredient}, try using: {substitutions_list}. Do any of these work for you?"
        ],

        'recipe_missing_ingredients': [
            "For {recipe_name}, you're missing: {missing_list}. Which ingredient would you like a substitute for?",
            "You need {missing_count} more ingredients for {recipe_name}: {missing_list}. Would you like substitutes for any of these?",
            "To make {recipe_name}, you still need: {missing_list}. I can help find substitutes if you're missing any of these."
        ],

        'apply_substitution': [
            "I've updated the recipe to use {substitute} instead of {ingredient}. {notes}",
            "Great! {substitute} will work in place of {ingredient}. {notes}",
            "I've substituted {ingredient} with {substitute}. {notes}"
        ],

        # Add or update these templates in your response generator

        'multiple_recipes_found': [
            "I found {recipe_count} recipes that match your ingredients:\n\n{recipe_list}\n\nWhich one would you like to try? Just say the number or name.",
            "Based on your available ingredients, you could make:\n\n{recipe_list}\n\nWhich recipe interests you? Tell me the number or name.",
            "Here are some recipes you can make with your ingredients:\n\n{recipe_list}\n\nWhich recipe would you like to see? You can say the number or name."
        ],

        'recipe_selected': [
            "Great choice! {recipe_name} uses {match_percentage}% of your available ingredients. You have {matched_count} of the required ingredients and are missing {missing_count}: {missing_list}. Would you like to see the full recipe?",
            "You selected {recipe_name}. You already have {matched_count} ingredients for this recipe and are missing {missing_count}: {missing_list}. Ready to see the complete recipe?",
            "{recipe_name} is a good choice! You have {match_percentage}% of the ingredients needed. Missing: {missing_list}. Would you like to see the complete recipe?"
        ],

        'invalid_recipe_selection': [
            "That selection isn't valid. Please choose a recipe number from 1 to {total_recipes}, or specify the name of one of the suggested recipes.",
            "I don't see that recipe in the options. Choose a number from 1-{total_recipes} or tell me the name of the recipe you want to see.",
            "I couldn't find that recipe in the list. Please select a number between 1 and {total_recipes}, or say the name of one of the recipes I suggested."
        ],

        'recipe_selection_unclear': [
            "I'm not sure which recipe you want to select. Please choose a recipe by number (1-{recipe_count}) or by name.",
            "Could you clarify which recipe you'd like to see? You can say the number (like 'recipe 2') or the name of the recipe.",
            "I didn't catch which recipe you want. Please specify by saying the number or name of one of the recipes I suggested."
        ],

        'recipe_search_error': [
            "I'm having trouble searching for recipes right now. The error was: {error}. Please try again.",
            "Something went wrong while searching for recipes: {error}. Let's try again.",
            "There was an error in the recipe search: {error}. Please try once more."
        ],

        'recipe_details_request': [
            "Would you like to see the full recipe for {recipe_name}?",
            "Ready to view the complete {recipe_name} recipe?",
            "Shall I show you the detailed recipe for {recipe_name}?"
        ],


        'substitution_options': [
            "For {ingredient}, you could use: {substitutions_list}. Would you like to use one of these substitutes?",
            "No {ingredient}? You can substitute it with: {substitutions_list}. Which would you prefer to use?",
            "Instead of {ingredient}, try using: {substitutions_list}. Do any of these work for you?"
        ],

        'no_substitution_found': [
            "I don't have specific substitutions for {ingredient} in my database. You could try searching online for alternatives or continue with the recipe without it if it's not essential.",
            "I don't know any direct substitutes for {ingredient}. You might want to search online or skip this ingredient if it's not crucial to the recipe.",
            "Sorry, I don't have substitution suggestions for {ingredient}. Consider checking online for alternatives or proceeding without it if possible."
        ],

        'list_recipe_ingredients': [
            "For {recipe_name}, you'll need: {ingredients_list}. Which ingredient would you like a substitute for?",
            "The {recipe_name} recipe requires: {ingredients_list}. Do you need a substitute for any of these?",
            "Here are the ingredients for {recipe_name}: {ingredients_list}. Let me know if you need a substitute for any of them."
        ],

        'reset_complete': [
            "I've reset our conversation. What ingredients do you have available?",
            "Starting over! Tell me what ingredients you have in your kitchen.",
            "Let's begin fresh! What ingredients would you like to cook with?"
        ],

        'reset_with_ingredients': [
            "I've reset our conversation but kept your ingredients: {ingredients_list}. What would you like to do now?",
            "Starting over with your current ingredients: {ingredients_list}. Would you like to search for recipes?",
            "I've reset the conversation. You still have {ingredients_list} available. What would you like to do next?"
        ],

        'recipe_selection_error': [
            "I ran into an issue selecting that recipe: {error}. Could you try selecting a different one?",
            "There was a problem with that recipe selection: {error}. Please try another option.",
            "I couldn't select that recipe due to an error: {error}. Try choosing a different one."
        ],

        'ingredient_quantities': [
            "Here are the quantities for {recipe_name}:\n\n{quantities_list}",
            "For {recipe_name}, here are the ingredient measurements:\n\n{quantities_list}",
            "The {recipe_name} recipe requires these quantities:\n\n{quantities_list}"
        ],

        'no_quantities_available': [
            "I'm sorry, I don't have specific quantity information for {recipe_name}. The recipe only lists ingredients without measurements.",
            "The {recipe_name} recipe doesn't specify exact quantities. You might need to use these ingredients to taste.",
            "Unfortunately, I don't have detailed measurements for {recipe_name}. The recipe only provides the ingredient list without quantities."
        ]
            }
    
    # Select a random template for the response type
    if response_type in templates:
        template = random.choice(templates[response_type])
    else:
        # Fallback for undefined response types
        return "I'm not sure how to respond to that. Can you try phrasing it differently?"
    
    # Format the template with the provided data
    try:
        # Process specific data formatting for certain response types
        if response_type == 'ingredients_added' or response_type == 'ingredients_added_suggest_search':
            ingredients = data.get('ingredients', [])
            data['ingredients_list'] = ', '.join(ingredients)
            data['total_count'] = len(ingredients)
        
        elif response_type == 'recipe_found':
            recipe = data.get('recipe', {})
            data['recipe_name'] = recipe.get('name', 'this recipe')
            
            matched = data.get('matched_ingredients', [])
            missing = data.get('missing_ingredients', [])
            
            total_ingredients = len(matched) + len(missing)
            match_percentage = round(len(matched) / total_ingredients * 100) if total_ingredients > 0 else 0
            
            data['match_count'] = len(matched)
            data['missing_count'] = len(missing)
            data['total_ingredients'] = total_ingredients
            data['match_percentage'] = match_percentage
            data['missing_list'] = ', '.join(missing[:3]) + ('...' if len(missing) > 3 else '')
        
        # Update the recipe_details case in your response generator

        elif response_type == 'recipe_details':
            recipe = data.get('recipe', {})
            data['recipe_name'] = recipe.get('name', 'this recipe')
            
            # Format recipe details
            details = []
            
            # Add ingredients with proper formatting
            if 'formatted_ingredients' in recipe and recipe['formatted_ingredients']:
                details.append("📋 Ingredients:")
                for ing in recipe['formatted_ingredients']:
                    if ing.get('quantity'):
                        details.append(f"• {ing['quantity']} {ing['name']}")
                    else:
                        details.append(f"• {ing['original']}")
                details.append("")
            elif 'ingredients' in recipe:
                details.append("📋 Ingredients:")
                for ingredient in recipe['ingredients']:
                    # Try to extract quantity on the fly if not pre-parsed
                    import re
                    quantity_match = re.match(r'^([\d\s./]+\s*[a-zA-Z]*)\s+(.+)$', ingredient)
                    if quantity_match:
                        quantity = quantity_match.group(1).strip()
                        name = quantity_match.group(2).strip()
                        details.append(f"• {quantity} {name}")
                    else:
                        details.append(f"• {ingredient}")
                details.append("")
            
            # Add instructions with step numbers
            if 'instructions' in recipe:
                details.append("📝 Instructions:")
                for i, step in enumerate(recipe['instructions']):
                    details.append(f"{i+1}. {step}")
            
            # Add cooking time if available
            if 'minutes' in recipe:
                minutes = recipe['minutes']
                if minutes:
                    try:
                        minutes_val = int(minutes)
                        hours = minutes_val // 60
                        mins = minutes_val % 60
                        if hours > 0:
                            time_str = f"{hours} hour{'s' if hours > 1 else ''}"
                            if mins > 0:
                                time_str += f" {mins} minute{'s' if mins > 1 else ''}"
                        else:
                            time_str = f"{mins} minute{'s' if mins > 1 else ''}"
                        details.append(f"\n⏱️ Total Time: {time_str}")
                    except (ValueError, TypeError):
                        details.append(f"\n⏱️ Total Time: {minutes} minutes")
            
            # Add serving information if available
            if 'n_servings' in recipe or 'servings' in recipe:
                servings = recipe.get('n_servings', recipe.get('servings', None))
                if servings:
                    details.append(f"👥 Servings: {servings}")
            
            # Add substitution notes if any
            if 'substitutions' in recipe and recipe['substitutions']:
                details.append("\n🔄 Substitution Notes:")
                for sub in recipe['substitutions']:
                    if isinstance(sub, dict):
                        original = sub.get('original', '')
                        substitute = sub.get('substitute', '')
                        notes = sub.get('notes', '')
                        details.append(f"• Use {substitute} instead of {original}. {notes}")
                    else:
                        details.append(f"• {sub}")
            
            data['recipe_details'] = '\n'.join(details)
                
        elif response_type == 'substitution_suggested':
            substitutions = data.get('substitutions', [])
            subs_list = []
            
            for sub in substitutions[:3]:  # Limit to top 3
                if isinstance(sub, dict):
                    sub_text = sub.get('substitute', '')
                    if 'notes' in sub and sub['notes']:
                        sub_text += f" ({sub['notes']})"
                else:
                    sub_text = str(sub)
                subs_list.append(sub_text)
            
            data['substitutions_list'] = ', '.join(subs_list)
        
        elif response_type == 'recipe_enhancement':
            suggestions = data.get('suggestions', [])
            suggestions_list = []
            
            for suggestion in suggestions[:3]:  # Limit to top 3
                if isinstance(suggestion, dict):
                    suggestion_text = suggestion.get('ingredient', '')
                    if 'reason' in suggestion and suggestion['reason']:
                        suggestion_text += f" ({suggestion['reason']})"
                else:
                    suggestion_text = str(suggestion)
                suggestions_list.append(suggestion_text)
            
            data['suggestions_list'] = ', '.join(suggestions_list)
        
        elif response_type == 'recipe_adapted_for_diet':
            substitutions = data.get('substitutions', [])
            subs_list = []
            
            for sub in substitutions[:3]:  # Limit to top 3
                if isinstance(sub, dict):
                    original = sub.get('original', '')
                    substitute = sub.get('substitute', '')
                    subs_list.append(f"{original} → {substitute}")
                else:
                    subs_list.append(str(sub))
            
            data['substitutions_list'] = ', '.join(subs_list)
            
            # Format restrictions list
            restrictions = data.get('restrictions', [])
            if isinstance(restrictions, list):
                data['restrictions'] = ', '.join(restrictions)
        
        elif response_type == 'dietary_restriction_noted':
            # Format restrictions list
            restrictions = data.get('restrictions', [])
            if isinstance(restrictions, list):
                data['restrictions'] = ', '.join(restrictions)
            elif not isinstance(restrictions, str):
                data['restrictions'] = str(restrictions)
        
        # Format the template with the processed data
        # Add this to your response_generator.py to format recipe lists

        # Update this in your response_generator.py to format recipe lists

        elif response_type == 'multiple_recipes_found':
            recipes = data.get('recipes', [])
            data['recipe_count'] = len(recipes)
            
            # Format recipe list
            recipe_list_items = []
            for recipe in recipes:
                recipe_list_items.append(
                    f"{recipe['index']}. {recipe['name']} - {recipe['match_percentage']}% match "
                    f"({recipe['matched_count']}/{recipe['total_count']} ingredients)"
                )
            
            data['recipe_list'] = '\n'.join(recipe_list_items)
        return template.format(**data)
    
    except KeyError as e:
        print(f"Error formatting response: Missing data key {e}")
        return f"I'm having trouble processing that information. Could you try again with different wording?"
    
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I encountered an error while generating a response. Could you try again?"

# Test function if run directly
if __name__ == "__main__":
    # Test recipe found
    test_recipe = {
        'name': 'Simple Pancakes',
        'ingredients': ['1 cup flour', '2 tablespoons sugar', '1 egg', '1 cup milk', '2 tablespoons butter'],
        'instructions': [
            'Mix dry ingredients.',
            'Add wet ingredients and mix until smooth.',
            'Heat a pan and add a little butter.',
            'Pour batter and cook until bubbles form.',
            'Flip and cook other side until golden.'
        ]
    }
    
    test_contexts = [
        ('recipe_found', {
            'recipe': test_recipe,
            'matched_ingredients': ['flour', 'sugar', 'egg'],
            'missing_ingredients': ['milk', 'butter'],
            'score': 0.6
        }),
        ('recipe_details', {
            'recipe': test_recipe,
            'substitutions': {'milk': 'water', 'butter': 'oil'}
        }),
        ('substitution_found', {
            'ingredient': 'butter',
            'substitute': 'olive oil',
            'ratio': 0.75,
            'notes': 'Use 3/4 the amount for best results.'
        }),
        ('no_recipes_found', {
            'ingredients': ['ketchup', 'mustard', 'pickles']
        }),
        ('help', {
            'has_recipe': True
        }),
        ('next_step', {
            'previous_step': 'Mix dry ingredients.',
            'current_step': 'Add wet ingredients and mix until smooth.',
            'step_number': 2,
            'total_steps': 5
        }),
        ('ingredient_quantity', {
            'ingredient': 'flour',
            'quantity': '1 cup flour'
        }),
        ('unknown_with_recipe', {
            'recipe_name': 'Simple Pancakes'
        })
    ]
    
    print("Testing response generator with different contexts:\n")
    for response_type, context in test_contexts:
        print(f"RESPONSE TYPE: {response_type}")
        print(f"CONTEXT: {context}")
        response = generate_response(response_type, context)
        print(f"RESPONSE: {response}\n")
        print("-" * 80 + "\n")