# food_rescuer/conversation/state_manager.py
# Manages the conversation state and flow for the Food Rescuer assistant

import os
import sys

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conversation.response_generator import generate_response
from models.intent_classifier import IntentClassifier
from models.recipe_retrieval import RecipeRetriever
from recipe.recipe_adapter import RecipeAdapter
from data.food_substitutions import SubstitutionKnowledgeBase

# Update your ConversationState class to support the improved recipe selection flow

class ConversationState:
    """Holds the current state of a conversation"""
    
    def __init__(self):
        """Initialize conversation state"""
        self.available_ingredients = []  # Ingredients the user has
        self.current_recipe = None  # Currently selected recipe
        self.current_step_index = 0  # Current step in the recipe
        self.substitutions_made = {}  # Ingredient -> substitute mappings
        self.missing_ingredients = []  # Ingredients the user doesn't have
        self.suggested_recipes = []  # List of suggested recipes as (recipe, score, matched, missing) tuples
        self.selected_recipe_index = None  # Index of the selected recipe
        self.dietary_restrictions = []  # Dietary restrictions
        self.context = {
            "last_intent": None,
            "previous_utterance": None,
            "recipe_details_requested": False,
            "last_action": None
        }  # Additional context for managing conversation flow
    
    def update_available_ingredients(self, ingredients):
        """Add ingredients to the available list"""
        for ingredient in ingredients:
            if ingredient.lower() not in [i.lower() for i in self.available_ingredients]:
                self.available_ingredients.append(ingredient)
    
    # def set_current_recipe(self, recipe, index=None):
    #     """Set the current recipe being discussed"""
    #     self.current_recipe = recipe
    #     self.current_step_index = 0
    #     self.selected_recipe_index = index
    #     self.context["recipe_details_requested"] = False
    #     self.context["last_action"] = "recipe_selected"

    def set_current_recipe(self, recipe, index=None):
        """Set the current recipe being discussed and extract its ingredients"""
        self.current_recipe = recipe
        self.current_step_index = 0
        self.selected_recipe_index = index
        self.context["recipe_details_requested"] = False
        self.context["last_action"] = "recipe_selected"
        
        # Extract and track needed ingredients
        self.needed_ingredients = []
        if recipe and 'ingredients' in recipe:
            for ingredient in recipe['ingredients']:
                # Clean up ingredient text to get base ingredient
                import re
                # Try to remove quantities and find base ingredient
                base_ingredient_match = re.search(r'(?:[\d\s./]+\s*[a-zA-Z]*\s+)?([a-zA-Z\s]+)(?:\s*,.*)?$', ingredient)
                if base_ingredient_match:
                    base_ingredient = base_ingredient_match.group(1).strip().lower()
                    self.needed_ingredients.append({
                        'name': base_ingredient,
                        'original': ingredient,
                        'have': base_ingredient.lower() in [i.lower() for i in self.available_ingredients]
                    })
                else:
                    self.needed_ingredients.append({
                        'name': ingredient.lower(),
                        'original': ingredient,
                        'have': ingredient.lower() in [i.lower() for i in self.available_ingredients]
                    })
                
            # Update missing ingredients based on recipe
            self.missing_ingredients = [
                item['name'] for item in self.needed_ingredients 
                if not item['have']
            ]
    
    def set_suggested_recipes(self, recipes):
        """Set the list of suggested recipes"""
        self.suggested_recipes = recipes
        self.selected_recipe_index = None
        self.current_recipe = None  # Clear current recipe when showing suggestions
        self.context["last_action"] = "recipes_suggested"
    
    def request_recipe_details(self):
        """Mark that recipe details have been requested"""
        self.context["recipe_details_requested"] = True
        self.context["last_action"] = "recipe_details_requested"
    
    def next_step(self):
        """Move to the next step in the recipe"""
        if self.current_recipe and 'instructions' in self.current_recipe:
            if self.current_step_index < len(self.current_recipe['instructions']) - 1:
                self.current_step_index += 1
                self.context["last_action"] = "next_step"
                return True
        return False
    
    def previous_step(self):
        """Move to the previous step in the recipe"""
        if self.current_recipe and 'instructions' in self.current_recipe:
            if self.current_step_index > 0:
                self.current_step_index -= 1
                self.context["last_action"] = "previous_step"
                return True
        return False
    
    def get_current_step(self):
        """Get the current instruction step"""
        if self.current_recipe and 'instructions' in self.current_recipe:
            if 0 <= self.current_step_index < len(self.current_recipe['instructions']):
                return self.current_recipe['instructions'][self.current_step_index]
        return None
    
    def add_substitution(self, ingredient, substitute):
        """Record a substitution that was made"""
        self.substitutions_made[ingredient.lower()] = substitute.lower()
        self.context["last_action"] = "substitution_added"
    
    def add_missing_ingredient(self, ingredient):
        """Add an ingredient to the missing list"""
        ingredient_lower = ingredient.lower()
        if ingredient_lower not in [i.lower() for i in self.missing_ingredients]:
            self.missing_ingredients.append(ingredient)
            
            # Remove from available if it was mistakenly added
            self.available_ingredients = [i for i in self.available_ingredients 
                                         if i.lower() != ingredient_lower]
            self.context["last_action"] = "missing_ingredient_added"
    
    def add_dietary_restriction(self, restriction):
        """Add a dietary restriction"""
        if restriction.lower() not in [r.lower() for r in self.dietary_restrictions]:
            self.dietary_restrictions.append(restriction)
            self.context["last_action"] = "dietary_restriction_added"
    
    def reset(self):
        """Reset the conversation state"""
        self.__init__()

class ConversationManager:
    """Manages the conversation flow and state transitions"""
    
    def __init__(self, substitution_kb=None, recipe_retriever=None, intent_classifier=None):
        """
        Initialize the conversation manager
        
        Args:
            substitution_kb: Optional SubstitutionKnowledgeBase instance
            recipe_retriever: Optional RecipeRetriever instance
            intent_classifier: Optional IntentClassifier instance
        """
        # Initialize components
        self.substitution_kb = substitution_kb or SubstitutionKnowledgeBase()
        self.recipe_retriever = recipe_retriever or RecipeRetriever()
        self.intent_classifier = intent_classifier or IntentClassifier()
        self.recipe_adapter = RecipeAdapter(self.substitution_kb)
        
        # Initialize conversation state
        self.state = ConversationState()
    
    # Update your process method in ConversationManager to handle new intents and improve flow

    def process(self, text):
        """
        Process user input and generate a response
        
        Args:
            text: User input text
            
        Returns:
            str: Response to the user
        """
        # Save the previous utterance for context
        if hasattr(self, 'state') and hasattr(self.state, 'context'):
            self.state.context['previous_utterance'] = text
        
        # Check for reset commands before any other processing
        reset_phrases = ['start over', 'reset', 'begin again', 'new conversation', 'restart']
        if any(phrase in text.lower() for phrase in reset_phrases):
            # Create basic entities with just the text
            entities = {'text': text}
            return self._handle_reset(entities)
        
        # Check for quantity-related requests
        quantity_phrases = [
            'quantities', 'quantity', 'how much', 'how many', 
            'amount', 'amounts', 'measurements', 'serving size'
        ]
        if any(phrase in text.lower() for phrase in quantity_phrases) and self.state.current_recipe:
            return self._handle_ingredient_quantities()
        
        # Extract entities first to enhance intent detection
        try:
            from utils.entity_extraction import extract_entities, extract_recipe_selection
            entities = extract_entities(text)
            
            # Add recipe selection entities
            recipe_entities = extract_recipe_selection(text)
            entities.update(recipe_entities)
        except Exception as e:
            print(f"Error extracting entities: {e}")
            entities = {}
        
        # Add the original text to entities for context
        entities['text'] = text
        
        # Classify the intent
        intent_data = self.intent_classifier.classify(text)
        intent = intent_data['intent']
        
        # Add extracted entities from intent classifier
        if 'entities' in intent_data:
            for key, value in intent_data['entities'].items():
                if key not in entities:
                    entities[key] = value
        
        # Log the processed entities for debugging
        print(f"[Debug] Extracted entities: {entities}")
        
        # Special case handling for substitution requests - check for keywords
        substitution_phrases = ["substitut", "instead of", "don't have", "dont have", "missing", "no ", "without "]
        if any(phrase in text.lower() for phrase in substitution_phrases):
            return self._handle_request_substitution(entities)
        
        # Special case handling for dietary restrictions
        dietary_phrases = ["vegetarian", "vegan", "gluten free", "gluten-free", "dairy free", "dairy-free", "nut free", "nut-free"]
        if any(phrase in text.lower() for phrase in dietary_phrases) and 'dietary_restrictions' in entities:
            return self._handle_dietary_restrictions(entities)
        
        # Process based on intent
        if intent == 'search_by_ingredients':
            return self._perform_recipe_search()
        
        elif intent == 'declare_ingredients':
            return self._handle_declare_ingredients(entities)
        
        elif intent == 'get_recipe_details':
            # Check if we're in a state where we need to select a recipe first
            if self.state.suggested_recipes and not self.state.current_recipe:
                # User likely wants to see details of a specific recipe from the list
                return self._handle_select_recipe(entities)
            else:
                # User wants details of the currently selected recipe
                return self._handle_get_recipe_details()
        
        elif intent == 'select_recipe':
            return self._handle_select_recipe(entities)
        
        elif intent == 'show_more_recipes':
            return self._handle_show_more_recipes()
        
        elif intent == 'request_substitution':
            return self._handle_request_substitution(entities)
        
        elif intent == 'next_step':
            return self._handle_next_step()
        
        elif intent == 'previous_step':
            return self._handle_previous_step()
        
        elif intent == 'affirm':  # For "yes" responses
            # Check context to determine appropriate action
            if self.state.suggested_recipes and not self.state.current_recipe:
                # User said yes to seeing a recipe from the list - select the first one
                entities['recipe_number'] = 1
                return self._handle_select_recipe(entities)
            elif self.state.current_recipe and 'recipe_details_requested' in self.state.context:
                # User said yes to seeing full recipe details
                return self._handle_get_recipe_details()
            else:
                return self._handle_affirm(entities)
        
        elif intent == 'deny':  # For "no" responses
            return self._handle_deny(entities)
        
        elif intent == 'greeting':
            return self._handle_greeting(entities)
        
        elif intent == 'request_help':
            return self._handle_request_help()
        
        else:  # unknown intent
            # Direct recipe number selection (like just typing "2")
            if text.strip().isdigit() and self.state.suggested_recipes:
                entities['recipe_number'] = text.strip()
                return self._handle_select_recipe(entities)
            
            # Handle "show other recipes" or "show more recipes" requests
            if ("show" in text.lower() and 
                ("other" in text.lower() or "more" in text.lower()) and 
                "recipe" in text.lower()):
                return self._handle_show_more_recipes()
            
            # Check for recipe selection based on text content
            if "recipe" in text.lower() and any(str(i+1) in text for i in range(5)) and self.state.suggested_recipes:
                return self._handle_select_recipe(entities)
            
            # If we have suggested recipes but no selection, treat as a possible recipe selection
            elif self.state.suggested_recipes and not self.state.current_recipe:
                # Try to match against recipe names
                for i, result in enumerate(self.state.suggested_recipes):
                    if isinstance(result, tuple) and len(result) > 0:
                        recipe = result[0]
                    else:
                        recipe = result
                    
                    if recipe.get('name', '').lower() in text.lower():
                        entities['recipe_number'] = i + 1
                        return self._handle_select_recipe(entities)
                
                # If still no match, ask for clarification
                return generate_response('recipe_selection_unclear', {
                    'recipe_count': len(self.state.suggested_recipes)
                })
            
            else:
                return self._handle_unknown()
    
    def _handle_dietary_restrictions(self, entities):
        """
        Handle user's dietary restrictions
        
        Args:
            entities: Entities extracted from user input
            
        Returns:
            str: Response acknowledging dietary restrictions
        """
        if 'dietary_restrictions' in entities:
            restrictions = entities['dietary_restrictions']
            
            # Add to state
            for restriction in restrictions:
                self.state.add_dietary_restriction(restriction)
            
            # If we have a current recipe, check if it's compatible
            if self.state.current_recipe:
                recipe_name = self.state.current_recipe.get('name', 'this recipe')
                incompatible = False
                
                # Simple check for common restrictions
                for restriction in restrictions:
                    if restriction.lower() == 'vegetarian':
                        meat_ingredients = ['chicken', 'beef', 'pork', 'lamb', 'bacon', 'ham', 'sausage', 'turkey', 'fish', 'seafood', 'shrimp', 'scallops']
                        for ingredient in meat_ingredients:
                            if any(ingredient in ing.lower() for ing in self.state.current_recipe.get('ingredients', [])):
                                incompatible = True
                                break
                    
                    elif restriction.lower() == 'vegan':
                        animal_ingredients = ['chicken', 'beef', 'pork', 'lamb', 'bacon', 'ham', 'sausage', 'turkey', 'fish', 'seafood', 'milk', 'cheese', 'cream', 'butter', 'egg', 'honey', 'yogurt']
                        for ingredient in animal_ingredients:
                            if any(ingredient in ing.lower() for ing in self.state.current_recipe.get('ingredients', [])):
                                incompatible = True
                                break
                
                if incompatible:
                    return generate_response('recipe_not_compatible', {
                        'recipe_name': recipe_name,
                        'restrictions': ', '.join(restrictions)
                    })
                else:
                    return generate_response('recipe_compatible', {
                        'recipe_name': recipe_name,
                        'restrictions': ', '.join(restrictions)
                    })
            
            # No current recipe, just acknowledge
            return generate_response('dietary_restriction_noted', {
                'restrictions': ', '.join(restrictions)
            })
    
        return generate_response('dietary_restriction_unclear', {})

    def _handle_search_by_ingredients(self, entities):
        """Handle search by ingredients intent"""
        if 'ingredients' in entities and entities['ingredients']:
            # Update available ingredients
            self.state.update_available_ingredients(entities['ingredients'])
            
            # Find recipes matching the ingredients
            results = self.recipe_retriever.find_recipes(
                self.state.available_ingredients,
                max_results=5,
                min_ingredients_matched=1
            )
            
            if results:
                # Save the suggested recipes
                self.state.set_suggested_recipes(results)
                
                # Set the current recipe to the first result
                first_recipe, score, matched, missing = results[0]
                self.state.set_current_recipe(first_recipe, 0)
                
                # Update missing ingredients
                for ingredient in missing:
                    self.state.add_missing_ingredient(ingredient)
                
                # Generate response with recipe suggestions
                return generate_response('recipe_found', {
                    'recipe': first_recipe,
                    'recipes': results,
                    'matched_ingredients': matched,
                    'missing_ingredients': missing,
                    'score': score
                })
            else:
                return generate_response('no_recipes_found', {
                    'ingredients': self.state.available_ingredients
                })
        else:
            return generate_response('ask_for_ingredients', {})
    
    def _handle_declare_ingredients(self, entities):
        """Handle user declaring available ingredients"""
        if 'ingredients' in entities and entities['ingredients']:
            # Update available ingredients
            self.state.update_available_ingredients(entities['ingredients'])
            
            # If we have enough ingredients, suggest looking for recipes
            if len(self.state.available_ingredients) >= 3:
                return generate_response('ingredients_added_suggest_search', {
                    'ingredients': self.state.available_ingredients
                })
            else:
                return generate_response('ingredients_added', {
                    'ingredients': self.state.available_ingredients
                })
        else:
            return generate_response('ask_for_ingredients', {})
    
    def _handle_get_recipe_details(self):
        """Handle request for recipe details"""
        if self.state.current_recipe:
            return generate_response('recipe_details', {
                'recipe': self.state.current_recipe,
                'substitutions': self.state.substitutions_made
            })
        else:
            return generate_response('no_current_recipe', {})
    
    def _handle_request_substitution(self, entities):
        """
        Handle request for ingredient substitution with improved logic
        
        Args:
            entities: Entities extracted from user input
            
        Returns:
            str: Response with substitution suggestions
        """
        # Extract the missing ingredient from entities
        missing_ingredient = None
        
        if 'missing_ingredients' in entities and entities['missing_ingredients']:
            missing_ingredient = entities['missing_ingredients'][0]
        elif 'ingredient' in entities and entities['ingredient']:
            missing_ingredient = entities['ingredient']
        
        if not missing_ingredient:
            # Try to extract from the text
            text = entities.get('text', '').lower()
            
            # Check for phrases like "substitute for X" or "I don't have X"
            for phrase in ["substitute for ", "instead of ", "don't have ", "missing "]:
                if phrase in text:
                    after_phrase = text.split(phrase, 1)[1].strip()
                    words = after_phrase.split()
                    if words:
                        missing_ingredient = words[0].strip('.,;!?')
                        # If there are multiple words, take up to 3 for compound ingredients
                        if len(words) > 1:
                            missing_ingredient = ' '.join(words[:min(3, len(words))]).strip('.,;!?')
                        break
            
            # If still not found and we have a recipe, check against recipe ingredients
            if not missing_ingredient and self.state.current_recipe and 'ingredients' in self.state.current_recipe:
                # Extract possible ingredient mentions from text
                words = text.split()
                for ingredient in self.state.current_recipe['ingredients']:
                    for word in words:
                        word = word.lower().strip('.,;!?')
                        if word in ingredient.lower() and len(word) > 3:  # Avoid short words
                            missing_ingredient = ingredient
                            break
                    if missing_ingredient:
                        break
        
        if missing_ingredient:
            # Add to missing ingredients
            self.state.add_missing_ingredient(missing_ingredient)
            
            # Get available substitutions from knowledge base
            substitutions = self.substitution_kb.get_substitutions_for_recipe_ingredient(
                missing_ingredient, 
                self.state.available_ingredients
            )
            
            if substitutions:
                # Format substitution suggestions
                sub_list = []
                for sub in substitutions[:3]:  # Limit to top 3
                    sub_notes = f" ({sub['notes']})" if 'notes' in sub and sub['notes'] else ""
                    sub_list.append(f"{sub['substitute']}{sub_notes}")
                
                return generate_response('substitution_options', {
                    'ingredient': missing_ingredient,
                    'substitutions': sub_list
                })
            else:
                # No substitutions found, suggest general alternatives
                return generate_response('no_substitution_found', {
                    'ingredient': missing_ingredient
                })
        else:
            # If we have a current recipe with missing ingredients, list them
            if self.state.current_recipe and self.state.missing_ingredients:
                return generate_response('recipe_missing_ingredients', {
                    'recipe_name': self.state.current_recipe.get('name', 'this recipe'),
                    'missing_ingredients': self.state.missing_ingredients
                })
            else:
                return generate_response('ask_what_ingredient_missing', {})

    # Update the _handle_select_recipe method in your ConversationManager

    def _handle_select_recipe(self, entity):
        """
        Handle selection of a specific recipe from the list with improved logic
        
        Args:
            entity: Entity containing recipe selection information
            
        Returns:
            str: Response with selected recipe summary
        """
        # Get recipe selection (by number or name)
        selection = None
        
        if 'recipe_number' in entity:
            try:
                # Convert to zero-based index
                selection = int(entity['recipe_number']) - 1
            except (ValueError, TypeError):
                pass
        
        elif 'recipe_name' in entity:
            # Find recipe by name
            recipe_name = entity['recipe_name'].lower()
            for i, (recipe, _, _, _) in enumerate(self.state.suggested_recipes):
                if recipe_name in recipe.get('name', '').lower():
                    selection = i
                    break
        
        # Try to infer from the user's input if no clear selection
        if selection is None and 'text' in entity:
            text = entity['text'].lower()
            
            # Look for recipe numbers
            import re
            number_patterns = [
                r'number\s+(\d+)',
                r'recipe\s+(\d+)',
                r'option\s+(\d+)',
                r'(\d+)(?:st|nd|rd|th)?'  # matches "1st", "2nd", "3", etc.
            ]
            
            for pattern in number_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        selection = int(match.group(1)) - 1
                        break
                    except (ValueError, TypeError):
                        pass
            
            # If still not found, look for recipe names in suggested recipes
            if selection is None:
                for i, (recipe, _, _, _) in enumerate(self.state.suggested_recipes):
                    recipe_name = recipe.get('name', '').lower()
                    if recipe_name in text:
                        selection = i
                        break
            
            # Last resort - check if the text is just a number
            if selection is None and text.isdigit():
                try:
                    selection = int(text) - 1
                except (ValueError, TypeError):
                    pass
        
        # Validate selection
        if selection is not None and 0 <= selection < len(self.state.suggested_recipes):
            # Get the selected recipe
            recipe, score, matched, missing = self.state.suggested_recipes[selection]
            
            # Set as current recipe
            self.state.set_current_recipe(recipe, selection)
            
            # Ensure we have the required data for the response template
            response_data = {
                'recipe_name': recipe.get('name', f"Recipe {selection+1}"),
                'matched_ingredients': matched,
                'missing_ingredients': missing,
                'missing_list': ', '.join(missing[:3]) + ('...' if len(missing) > 3 else ''),
                'matched_count': len(matched),
                'missing_count': len(missing),
                'match_percentage': round(len(matched) / (len(matched) + len(missing)) * 100) if (len(matched) + len(missing)) > 0 else 0
            }
            
            return generate_response('recipe_selected', response_data)
        else:
            # Invalid selection
            return generate_response('invalid_recipe_selection', {
                'total_recipes': len(self.state.suggested_recipes)
            })

    def _handle_get_recipe_details(self):
        """
        Handle request for recipe details with improved ingredient formatting
        
        Returns:
            str: Formatted recipe details
        """
        if not self.state.current_recipe:
            return generate_response('no_current_recipe', {})
        
        # Mark that recipe details have been requested
        self.state.request_recipe_details()
        
        # Check if we have formatted ingredients
        recipe = self.state.current_recipe
        
        # If we don't have formatted ingredients yet, try to format them
        if 'formatted_ingredients' not in recipe and hasattr(self, 'recipe_retriever'):
            try:
                # Get recipe ID or name for retrieval
                recipe_id = recipe.get('id')
                recipe_name = recipe.get('name')
                
                # Try to get a formatted version
                formatted_recipe = self.recipe_retriever.get_recipe_with_formatted_ingredients(
                    recipe_id=recipe_id, 
                    recipe_name=recipe_name
                )
                
                if formatted_recipe:
                    recipe = formatted_recipe
                    # Update the state
                    self.state.current_recipe = formatted_recipe
            except Exception as e:
                print(f"Error formatting recipe ingredients: {e}")
        
        # Generate response with properly formatted recipe
        return generate_response('recipe_details', {
            'recipe': recipe
        })
    
    def _handle_next_step(self):
        """Handle request for the next step in the recipe"""
        if not self.state.current_recipe:
            return generate_response('no_current_recipe', {})
        
        current_step = self.state.get_current_step()
        
        if current_step:
            if self.state.next_step():
                next_step = self.state.get_current_step()
                return generate_response('next_step', {
                    'previous_step': current_step,
                    'current_step': next_step,
                    'step_number': self.state.current_step_index + 1,
                    'total_steps': len(self.state.current_recipe.get('instructions', []))
                })
            else:
                return generate_response('recipe_completed', {
                    'recipe': self.state.current_recipe
                })
        else:
            return generate_response('no_steps_found', {})
    
    def _handle_previous_step(self):
        """Handle request for the previous step in the recipe"""
        if not self.state.current_recipe:
            return generate_response('no_current_recipe', {})
        
        if self.state.previous_step():
            current_step = self.state.get_current_step()
            return generate_response('previous_step', {
                'current_step': current_step,
                'step_number': self.state.current_step_index + 1,
                'total_steps': len(self.state.current_recipe.get('instructions', []))
            })
        else:
            return generate_response('first_step', {
                'current_step': self.state.get_current_step()
            })
    
    def _handle_confirm_ingredient(self, entities):
        """Handle confirmation of having an ingredient"""
        if 'ingredient' in entities and entities['ingredient']:
            ingredient = entities['ingredient']
            
            # Add to available ingredients
            self.state.update_available_ingredients([ingredient])
            
            # Check if this was previously missing
            was_missing = ingredient.lower() in [i.lower() for i in self.state.missing_ingredients]
            if was_missing:
                # Remove from missing ingredients
                self.state.missing_ingredients = [i for i in self.state.missing_ingredients 
                                               if i.lower() != ingredient.lower()]
                
                return generate_response('ingredient_now_available', {
                    'ingredient': ingredient
                })
            else:
                return generate_response('ingredient_confirmed', {
                    'ingredient': ingredient
                })
        else:
            return generate_response('ingredient_confirmation_unclear', {})
    
    def _handle_ingredient_quantities(self):
        """
        Handle requests specifically about ingredient quantities
        
        Returns:
            str: Response with ingredient quantities
        """
        if not self.state.current_recipe:
            return generate_response('no_current_recipe', {})
        
        recipe = self.state.current_recipe
        
        # Try to format the recipe if not already formatted
        if 'formatted_ingredients' not in recipe and hasattr(self, 'recipe_retriever'):
            try:
                # Get recipe ID or name for retrieval
                recipe_id = recipe.get('id')
                recipe_name = recipe.get('name')
                
                # Try to get a formatted version
                formatted_recipe = self.recipe_retriever.get_recipe_with_formatted_ingredients(
                    recipe_id=recipe_id, 
                    recipe_name=recipe_name
                )
                
                if formatted_recipe:
                    recipe = formatted_recipe
                    # Update the state
                    self.state.current_recipe = formatted_recipe
            except Exception as e:
                print(f"Error formatting recipe ingredients: {e}")
        
        # Extract ingredient quantities for display
        quantities_list = []
        
        if 'formatted_ingredients' in recipe and recipe['formatted_ingredients']:
            for ing in recipe['formatted_ingredients']:
                if ing.get('quantity') and ing.get('name'):
                    quantities_list.append(f"• {ing['quantity']} {ing['name']}")
                else:
                    quantities_list.append(f"• {ing.get('original', ing.get('name', 'Unknown ingredient'))}")
        else:
            # If no formatted ingredients, try to parse quantities from the ingredients on the fly
            for ingredient in recipe.get('ingredients', []):
                quantities_list.append(f"• {ingredient}")
        
        # Create response
        if quantities_list:
            return generate_response('ingredient_quantities', {
                'recipe_name': recipe.get('name', 'this recipe'),
                'quantities_list': '\n'.join(quantities_list)
            })
        else:
            return generate_response('no_quantities_available', {
                'recipe_name': recipe.get('name', 'this recipe')
            })

    def _handle_ask_ingredient_quantity(self, entities):
        """Handle question about ingredient quantity"""
        if not self.state.current_recipe:
            return generate_response('no_current_recipe', {})
        
        if 'ingredient' in entities and entities['ingredient']:
            ingredient = entities['ingredient']
            
            # Look for the ingredient in the recipe
            if 'ingredients' in self.state.current_recipe:
                for recipe_ingredient in self.state.current_recipe['ingredients']:
                    if ingredient.lower() in recipe_ingredient.lower():
                        return generate_response('ingredient_quantity', {
                            'ingredient': ingredient,
                            'quantity': recipe_ingredient
                        })
            
            # Ingredient not found in recipe
            return generate_response('ingredient_not_in_recipe', {
                'ingredient': ingredient,
                'recipe_name': self.state.current_recipe.get('name', 'this recipe')
            })
        else:
            return generate_response('ask_which_ingredient', {})
    
    def _handle_express_dietary_restriction(self, entities):
        """Handle expression of dietary restriction"""
        if 'restriction' in entities and entities['restriction']:
            restriction = entities['restriction']
            
            # Add to dietary restrictions
            self.state.add_dietary_restriction(restriction)
            
            return generate_response('dietary_restriction_noted', {
                'restriction': restriction
            })
        else:
            return generate_response('dietary_restriction_unclear', {})
    
    def _handle_request_help(self):
        """Handle request for help"""
        return generate_response('help', {
            'has_recipe': self.state.current_recipe is not None,
            'has_ingredients': len(self.state.available_ingredients) > 0
        })
    
    def _handle_recipe_completed(self):
        """Handle notification that recipe is completed"""
        if self.state.current_recipe:
            return generate_response('congratulate_completion', {
                'recipe_name': self.state.current_recipe.get('name', 'the recipe')
            })
        else:
            return generate_response('no_current_recipe', {})
    
    def _handle_recipe_feedback(self):
        """Handle recipe feedback"""
        if self.state.current_recipe:
            return generate_response('thank_for_feedback', {
                'recipe_name': self.state.current_recipe.get('name', 'the recipe')
            })
        else:
            return generate_response('general_thanks', {})

    # Add these new methods to your existing ConversationManager class in state_manager.py
    # Right after the _handle_recipe_feedback method, add:

    def _handle_affirm(self, entities):
        """Handle affirmative response (yes)"""
        # Check conversation context to determine appropriate action
        if len(self.state.available_ingredients) > 0 and not self.state.current_recipe:
            # User has ingredients but no recipe - they're probably saying yes to "do you want to search?"
            return self._perform_recipe_search()
        elif self.state.current_recipe and len(self.state.missing_ingredients) > 0:
            # If we were discussing substitutions, this might be confirming they want to proceed anyway
            return generate_response('proceed_with_recipe', {
                'recipe_name': self.state.current_recipe.get('name', 'this recipe')
            })
        else:
            # Generic affirmative response
            return generate_response('acknowledged', {})

    def _handle_deny(self, entities):
        """Handle negative response (no)"""
        # Check conversation context to determine appropriate action
        if len(self.state.available_ingredients) > 0 and not self.state.current_recipe:
            # User has ingredients but doesn't want to search
            return generate_response('no_search', {})
        elif self.state.current_recipe and len(self.state.missing_ingredients) > 0:
            # If we were discussing substitutions, this might be declining to proceed
            return generate_response('suggest_different_recipe', {})
        else:
            # Generic negative response
            return generate_response('acknowledged_negative', {})

    def _handle_greeting(self, entities):
        """Handle greeting"""
        return generate_response('greeting', {
            'has_ingredients': len(self.state.available_ingredients) > 0,
            'has_recipe': self.state.current_recipe is not None
        })

    # def _perform_recipe_search(self):
    #     """Search for recipes with available ingredients"""
    #     if not self.state.available_ingredients:
    #         return generate_response('ask_for_ingredients', {})
        
    #     # Find recipes matching the ingredients
    #     results = self.recipe_retriever.find_recipes(
    #         self.state.available_ingredients,
    #         max_results=5,
    #         min_ingredients_matched=1
    #     )
        
    #     if results:
    #         # Save the suggested recipes
    #         self.state.set_suggested_recipes(results)
            
    #         # Set the current recipe to the first result
    #         first_recipe, score, matched, missing = results[0]
    #         self.state.set_current_recipe(first_recipe, 0)
            
    #         # Update missing ingredients
    #         for ingredient in missing:
    #             self.state.add_missing_ingredient(ingredient)
            
    #         # Generate response with recipe suggestions
    #         return generate_response('recipe_found', {
    #             'recipe': first_recipe,
    #             'matched_ingredients': matched,
    #             'missing_ingredients': missing,
    #             'score': score
    #         })
    #     else:
    #         return generate_response('no_recipes_found', {
    #             'ingredients': self.state.available_ingredients
    #         })
        
    def _handle_discuss_ingredient(self, entities):
        """Handle general discussion about an ingredient"""
        if 'ingredients' in entities and entities['ingredients']:
            ingredient = entities['ingredients'][0]  # Take the first one
            
            # Add to available ingredients if it wasn't an explicit declaration
            self.state.update_available_ingredients([ingredient])
            
            return generate_response('discuss_ingredient', {
                'ingredient': ingredient,
                'total_ingredients': len(self.state.available_ingredients)
            })
        else:
            return generate_response('ask_for_ingredients', {})
    
    def _handle_unknown(self):
        """Handle unknown intent"""
        if self.state.current_recipe:
            return generate_response('unknown_with_recipe', {
                'recipe_name': self.state.current_recipe.get('name', 'the current recipe')
            })
        elif self.state.available_ingredients:
            return generate_response('unknown_with_ingredients', {
                'num_ingredients': len(self.state.available_ingredients)
            })
        else:
            return generate_response('unknown_initial', {})
    
    def get_state_summary(self):
        """Get a summary of the current conversation state"""
        summary = {
            'has_recipe': self.state.current_recipe is not None,
            'recipe_name': self.state.current_recipe.get('name') if self.state.current_recipe else None,
            'available_ingredients': self.state.available_ingredients,
            'missing_ingredients': self.state.missing_ingredients,
            'substitutions': self.state.substitutions_made,
            'current_step': self.state.current_step_index + 1 if self.state.current_recipe else 0,
            'total_steps': len(self.state.current_recipe.get('instructions', [])) if self.state.current_recipe else 0,
            'dietary_restrictions': self.state.dietary_restrictions
        }
        return summary
    # Add these new methods to your ConversationManager class

    # Improved substitution handling in ConversationManager

    def _handle_request_substitution(self, entities):
        """
        Handle request for ingredient substitution with improved recognition
        
        Args:
            entities: Entities extracted from user input
            
        Returns:
            str: Response with substitution suggestions
        """
        # Extract the missing ingredient from entities or text
        missing_ingredient = None
        
        # Check if we directly extracted a missing ingredient
        if 'missing_ingredients' in entities and entities['missing_ingredients']:
            missing_ingredient = entities['missing_ingredients'][0]
        
        # Check for "I don't have X" pattern
        if not missing_ingredient and 'text' in entities:
            text = entities['text'].lower()
            dont_have_patterns = [
                r"don'?t have ([a-z\s]+)",
                r"missing ([a-z\s]+)",
                r"need ([a-z\s]+)",
                r"substitute ([a-z\s]+)",
                r"instead of ([a-z\s]+)"
            ]
            
            import re
            for pattern in dont_have_patterns:
                match = re.search(pattern, text)
                if match:
                    missing_ingredient = match.group(1).strip()
                    break
        
        # If we have a recipe with ingredients but no specific ingredient mentioned,
        # look for the ingredient in the text
        if not missing_ingredient and self.state.current_recipe:
            recipe_ingredients = []
            if 'ingredients' in self.state.current_recipe:
                recipe_ingredients = self.state.current_recipe['ingredients']
            elif 'formatted_ingredients' in self.state.current_recipe:
                recipe_ingredients = [ing.get('name', ing.get('original', '')) 
                                    for ing in self.state.current_recipe['formatted_ingredients']]
            
            # Check if any ingredient from the recipe is mentioned in the text
            if 'text' in entities:
                text = entities['text'].lower()
                for ingredient in recipe_ingredients:
                    # Extract the base ingredient name (no quantities or preparation instructions)
                    import re
                    base_match = re.search(r'([a-z\s]+)', ingredient.lower())
                    if base_match:
                        base_ingredient = base_match.group(1).strip()
                        if base_ingredient in text and len(base_ingredient) > 3:  # Avoid short matches
                            missing_ingredient = base_ingredient
                            break
        
        if missing_ingredient:
            print(f"Identified missing ingredient: {missing_ingredient}")
            
            # Add to missing ingredients
            self.state.add_missing_ingredient(missing_ingredient)
            
            # Get basic substitutions
            substitutions = []
            
            # Try to get from our knowledge base
            if hasattr(self, 'substitution_kb'):
                try:
                    substitutions = self.substitution_kb.get_substitutions(missing_ingredient)
                except Exception as e:
                    print(f"Error getting substitutions: {e}")
            
            # If no substitutions yet, try to get defaults for common ingredients
            if not substitutions:
                common_substitutions = {
                    'butter': ['olive oil', 'coconut oil', 'applesauce'],
                    'milk': ['almond milk', 'soy milk', 'water'],
                    'eggs': ['applesauce', 'mashed banana', 'flax seeds mixed with water'],
                    'flour': ['almond flour', 'rice flour', 'corn starch'],
                    'sugar': ['honey', 'maple syrup', 'stevia'],
                    'cream': ['coconut cream', 'yogurt'],
                    'parsley': ['cilantro', 'basil', 'oregano'],
                    'garlic': ['garlic powder', 'shallots', 'onion'],
                    'onion': ['green onion', 'shallots', 'leeks'],
                    'stock': ['broth', 'bouillon cube with water'],
                    'rice': ['quinoa', 'couscous', 'barley'],
                    'dill': ['tarragon', 'fennel', 'thyme', 'basil'],
                    'pickle juice': ['vinegar with salt', 'lemon juice']
                }
                
                # Check for exact match
                if missing_ingredient.lower() in common_substitutions:
                    subs = common_substitutions[missing_ingredient.lower()]
                    substitutions = [{"substitute": sub, "ratio": 1.0, "notes": ""} for sub in subs]
                else:
                    # Check for partial match
                    for ing, subs in common_substitutions.items():
                        if ing in missing_ingredient.lower() or missing_ingredient.lower() in ing:
                            substitutions = [{"substitute": sub, "ratio": 1.0, "notes": ""} for sub in subs]
                            break
                
            if substitutions:
                # Format substitution suggestions
                sub_list = []
                for sub in substitutions[:3]:  # Limit to top 3
                    if isinstance(sub, dict):
                        substitute = sub.get('substitute', '')
                        notes = f" ({sub.get('notes', '')})" if 'notes' in sub and sub['notes'] else ""
                        sub_list.append(f"{substitute}{notes}")
                    else:
                        sub_list.append(str(sub))
                
                return generate_response('substitution_options', {
                    'ingredient': missing_ingredient,
                    'substitutions': sub_list,
                    'substitutions_list': ', '.join(sub_list)
                })
            else:
                # No substitutions found
                return generate_response('no_substitution_found', {
                    'ingredient': missing_ingredient
                })
        else:
            # If we have a current recipe, list its ingredients
            if self.state.current_recipe and 'ingredients' in self.state.current_recipe:
                ingredients = self.state.current_recipe['ingredients']
                return generate_response('list_recipe_ingredients', {
                    'recipe_name': self.state.current_recipe.get('name', 'this recipe'),
                    'ingredients': ingredients,
                    'ingredients_list': ', '.join(ingredients[:5]) + ('...' if len(ingredients) > 5 else '')
                })
            else:
                return generate_response('ask_what_ingredient_missing', {})

    def _handle_dietary_restriction(self, entities):
        """
        Handle user's dietary restrictions and adjust recipes accordingly
        
        Args:
            entities: Entities extracted from user input
            
        Returns:
            str: Response acknowledging the dietary restriction
        """
        if 'dietary_restrictions' in entities and entities['dietary_restrictions']:
            restrictions = entities['dietary_restrictions']
            
            # Add to dietary restrictions
            for restriction in restrictions:
                self.state.add_dietary_restriction(restriction)
            
            # If there's a current recipe, adjust it for the restrictions
            if self.state.current_recipe:
                adjusted_recipe = self.recipe_adapter.adjust_recipe_for_dietary_restrictions(
                    self.state.current_recipe,
                    restrictions
                )
                
                # If the recipe was modified, update it
                if adjusted_recipe.get('substitutions'):
                    self.state.set_current_recipe(adjusted_recipe)
                    
                    # Generate response
                    return generate_response('recipe_adapted_for_diet', {
                        'recipe_name': adjusted_recipe.get('name', 'this recipe'),
                        'restrictions': restrictions,
                        'substitutions': adjusted_recipe.get('substitutions', [])
                    })
            
            # Generic acknowledgment if no recipe or no adaptations needed
            return generate_response('dietary_restriction_noted', {
                'restrictions': restrictions
            })
        else:
            return generate_response('dietary_restriction_unclear', {})

    def _handle_recipe_enhancement(self, entities):
        """
        Handle request for recipe enhancement or improvement
        
        Args:
            entities: Entities extracted from user input
            
        Returns:
            str: Response with enhancement suggestions
        """
        if not self.state.current_recipe:
            return generate_response('no_current_recipe', {})
        
        # Get enhancement suggestions
        suggestions = self.recipe_adapter.suggest_complementary_ingredients(
            self.state.current_recipe,
            self.state.available_ingredients
        )
        
        if suggestions:
            return generate_response('recipe_enhancement', {
                'recipe_name': self.state.current_recipe.get('name', 'this recipe'),
                'suggestions': suggestions
            })
        else:
            return generate_response('no_enhancement_needed', {
                'recipe_name': self.state.current_recipe.get('name', 'this recipe')
            })

    # def _perform_recipe_search(self):
    #     """
    #     Search for recipes with available ingredients with improved logic
        
    #     Returns:
    #         str: Response with recipe suggestions
    #     """
    #     if not self.state.available_ingredients:
    #         return generate_response('ask_for_ingredients', {})
        
    #     # Consider dietary restrictions when searching
    #     dietary_restrictions = self.state.dietary_restrictions
        
    #     # Find recipes matching the ingredients
    #     results = self.recipe_retriever.find_recipes(
    #         self.state.available_ingredients,
    #         max_results=5,
    #         min_ingredients_matched=1
    #     )
        
    #     if results:
    #         # Filter results based on dietary restrictions if any
    #         if dietary_restrictions:
    #             filtered_results = []
    #             for result_tuple in results:
    #                 recipe, score, matched, missing = result_tuple
                    
    #                 # Check if recipe is compatible with dietary restrictions
    #                 is_compatible = True
    #                 for restriction in dietary_restrictions:
    #                     # Simple check - for a real app, you'd want more sophisticated checking
    #                     if restriction.lower() == 'vegetarian':
    #                         meat_keywords = ['beef', 'chicken', 'pork', 'lamb', 'bacon', 'fish']
    #                         if any(meat in ingredient.lower() for ingredient in recipe.get('ingredients', [])):
    #                             is_compatible = False
    #                             break
                        
    #                     elif restriction.lower() == 'vegan':
    #                         animal_keywords = ['meat', 'beef', 'chicken', 'pork', 'fish', 'milk', 'cream', 'butter', 'cheese', 'egg']
    #                         if any(animal in ingredient.lower() for ingredient in recipe.get('ingredients', [])):
    #                             is_compatible = False
    #                             break
                    
    #                 if is_compatible:
    #                     filtered_results.append(result_tuple)
                
    #             # Use filtered results if any, otherwise fall back to original results
    #             if filtered_results:
    #                 results = filtered_results
            
    #         # Save the suggested recipes
    #         self.state.set_suggested_recipes(results)
            
    #         # Set the current recipe to the first result
    #         first_recipe, score, matched, missing = results[0]
    #         self.state.set_current_recipe(first_recipe, 0)
            
    #         # Update missing ingredients
    #         for ingredient in missing:
    #             self.state.add_missing_ingredient(ingredient)
            
    #         # Check if we need to adapt the recipe for dietary restrictions
    #         if self.state.dietary_restrictions:
    #             adapted_recipe = self.recipe_adapter.adjust_recipe_for_dietary_restrictions(
    #                 first_recipe,
    #                 self.state.dietary_restrictions
    #             )
                
    #             if adapted_recipe.get('substitutions'):
    #                 self.state.set_current_recipe(adapted_recipe)
            
    #         # Generate response with recipe suggestions
    #         return generate_response('recipe_found', {
    #             'recipe': first_recipe,
    #             'recipes': results,
    #             'matched_ingredients': matched,
    #             'missing_ingredients': missing,
    #             'score': score,
    #             'dietary_friendly': bool(self.state.dietary_restrictions) and 'substitutions' not in first_recipe
    #         })
    #     else:
    #         return generate_response('no_recipes_found', {
    #             'ingredients': self.state.available_ingredients
    #         })
    # Update these methods in your ConversationManager class to better handle recipe listings

    # Updated _perform_recipe_search method

    def _perform_recipe_search(self):
        """
        Search for recipes with available ingredients and show multiple options
        
        Returns:
            str: Response with multiple recipe suggestions
        """
        if not self.state.available_ingredients:
            return generate_response('ask_for_ingredients', {})
        
        # Find recipes matching the ingredients
        try:
            results = self.recipe_retriever.find_recipes(
                self.state.available_ingredients,
                max_results=5,
                min_ingredients_matched=1
            )
            
            if results:
                # Save the suggested recipes without selecting one yet
                self.state.set_suggested_recipes(results)
                
                # Format the recipe list for display
                recipe_list = []
                for i, (recipe, score, matched, missing) in enumerate(results):
                    total_ingredients = len(matched) + len(missing)
                    match_percentage = round(len(matched) / total_ingredients * 100) if total_ingredients > 0 else 0
                    recipe_list.append({
                        "index": i + 1,
                        "name": recipe.get('name', f"Recipe {i+1}"),
                        "match_percentage": match_percentage,
                        "matched_count": len(matched),
                        "missing_count": len(missing),
                        "total_count": total_ingredients
                    })
                
                # Generate response with multiple recipe suggestions
                return generate_response('multiple_recipes_found', {
                    'recipes': recipe_list,
                    'recipe_count': len(recipe_list),
                    'ingredients': self.state.available_ingredients
                })
            else:
                return generate_response('no_recipes_found', {
                    'ingredients': self.state.available_ingredients
                })
        except Exception as e:
            print(f"Error in recipe search: {e}")
            return generate_response('recipe_search_error', {
                'error': str(e)
            })

    # Complete replacement for the _handle_select_recipe method

    def _handle_select_recipe(self, entity):
        """
        Handle selection of a specific recipe from the list with robust error handling
        
        Args:
            entity: Entity containing recipe selection information
            
        Returns:
            str: Response with selected recipe summary
        """
        # Get recipe selection (by number or name)
        selection = None
        
        if 'recipe_number' in entity:
            try:
                # Convert to zero-based index
                selection = int(entity['recipe_number']) - 1
            except (ValueError, TypeError):
                pass
        
        elif 'recipe_name' in entity:
            # Find recipe by name
            recipe_name = entity['recipe_name'].lower()
            for i, result in enumerate(self.state.suggested_recipes):
                recipe = result[0] if isinstance(result, tuple) and len(result) > 0 else result
                if recipe_name in recipe.get('name', '').lower():
                    selection = i
                    break
        
        # Try to infer from user's input if no clear selection
        if selection is None and 'text' in entity:
            text = entity['text'].lower()
            
            # Check if text is just a number (like "5")
            if text.isdigit():
                try:
                    selection = int(text) - 1
                except (ValueError, TypeError):
                    pass
            
            # Look for recipe numbers (like "recipe 3")
            import re
            number_matches = re.findall(r'recipe\s+(\d+)', text)
            if number_matches:
                try:
                    selection = int(number_matches[0]) - 1
                except (ValueError, TypeError):
                    pass
        
        # Validate selection
        if selection is not None and 0 <= selection < len(self.state.suggested_recipes):
            try:
                # Get the selected recipe with proper error handling
                result = self.state.suggested_recipes[selection]
                
                # Different structures may exist - handle tuple or dict
                if isinstance(result, tuple) and len(result) >= 4:
                    recipe, score, matched, missing = result
                elif isinstance(result, dict):
                    recipe = result.get('recipe', {})
                    matched = result.get('matched', [])
                    missing = result.get('missing', [])
                else:
                    # Fallback in case of unexpected structure
                    recipe = result
                    matched = []
                    missing = []
                    if hasattr(self.state, 'available_ingredients'):
                        # Try to infer matched/missing from available ingredients
                        recipe_ingredients = recipe.get('ingredients', [])
                        matched = [ing for ing in recipe_ingredients if ing.lower() in 
                                [a.lower() for a in self.state.available_ingredients]]
                        missing = [ing for ing in recipe_ingredients if ing.lower() not in 
                                [a.lower() for a in self.state.available_ingredients]]
                
                # Set as current recipe
                self.state.set_current_recipe(recipe, selection)
                
                # Prepare data for response template with proper fallbacks
                response_data = {
                    'recipe_name': recipe.get('name', f"Recipe {selection+1}"),
                    'matched_ingredients': matched,
                    'missing_ingredients': missing,
                    'missing_list': ', '.join(missing[:3]) + ('...' if len(missing) > 3 else ''),
                    'matched_count': len(matched),
                    'missing_count': len(missing),
                    'match_percentage': round(len(matched) / 
                                            (len(matched) + len(missing)) * 100) if (len(matched) + len(missing)) > 0 else 0
                }
                
                # Generate response
                return self._handle_get_recipe_details()
            
            except Exception as e:
                print(f"Error selecting recipe: {e}")
                return generate_response('recipe_selection_error', {
                    'error': str(e)
                })
        else:
            # Invalid selection
            return generate_response('invalid_recipe_selection', {
                'total_recipes': len(self.state.suggested_recipes)
            })

    def _handle_show_more_recipes(self):
        """
        Handle request to show more recipes or alternative suggestions
        
        Returns:
            str: Response with more recipe options
        """
        # If we already have suggested recipes, show them again
        if self.state.suggested_recipes:
            recipe_list = []
            for i, (recipe, score, matched, missing) in enumerate(self.state.suggested_recipes):
                match_percentage = round(len(matched) / (len(matched) + len(missing)) * 100)
                recipe_list.append({
                    "index": i + 1,
                    "name": recipe.get('name', f"Recipe {i+1}"),
                    "match_percentage": match_percentage,
                    "matched_count": len(matched),
                    "missing_count": len(missing),
                    "total_count": len(matched) + len(missing)
                })
            
            return generate_response('multiple_recipes_found', {
                'recipes': recipe_list,
                'ingredients': self.state.available_ingredients
            })
        else:
            # If no recipes have been suggested yet, perform a search
            return self._perform_recipe_search()
    
    def _handle_reset(self, entity=None):
        """
        Reset the conversation state to start over
        
        Args:
            entity: Optional entity data
            
        Returns:
            str: Response confirming reset
        """
        # Save any available ingredients before resetting
        saved_ingredients = self.state.available_ingredients.copy() if hasattr(self.state, 'available_ingredients') else []
        
        # Reset the state
        self.state.reset()
        
        # Decide if we should add back the ingredients
        keep_ingredients = False
        if entity and 'text' in entity:
            if 'keep ingredients' in entity['text'].lower() or 'same ingredients' in entity['text'].lower():
                keep_ingredients = True
        
        if keep_ingredients and saved_ingredients:
            self.state.update_available_ingredients(saved_ingredients)
            return generate_response('reset_with_ingredients', {
                'ingredients': saved_ingredients,
                'ingredients_list': ', '.join(saved_ingredients)
            })
        else:
            return generate_response('reset_complete', {})





# Test the conversation manager if run directly
if __name__ == "__main__":
    manager = ConversationManager()
    
    # Create a simple interactive test loop
    print("Food Rescuer Assistant")
    print("Type 'exit' to quit.")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        response = manager.process(user_input)
        print(f"\nAssistant: {response}")
        
        # Optionally, print the state summary for debugging
        # print("\nState:", manager.get_state_summary())