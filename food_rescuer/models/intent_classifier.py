# food_rescuer/models/intent_classifier.py
# Intent classification for understanding user queries

import re
import os
import json
import string
from collections import defaultdict



# food_rescuer/models/dl_intent_classifier.py
# Deep learning-based intent classifier using sentence embeddings

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
from sklearn.metrics.pairwise import cosine_similarity

class DeepLearningIntentClassifier:
    """
    Intent classifier using deep learning and sentence embeddings
    """
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize the deep learning intent classifier"""
        # Load the sentence transformer model
        try:
            self.model = SentenceTransformer(model_name)
            print(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            print(f"Error loading sentence transformer model: {e}")
            self.model = None
        
        # Intent examples with variations for training
        self.intent_examples = {
            'search_by_ingredients': [
                "What can I make with eggs and flour?",
                "Show me recipes with chicken and rice",
                "I have tomatoes, cheese, and basil, what can I cook?",
                "What recipes can I make with potatoes?",
                "Find recipes using salmon and lemon",
                "What can I cook with the ingredients I have?",
                "Show me dishes I can make with pasta",
                "Recipes with beef and vegetables",
                "Find me something to cook with apples",
                "What meals can I make with flour, eggs, and milk?",
                "Show recipes that use garlic and tomatoes",
                "I need a recipe that uses spinach",
                "What dishes can I prepare with ground beef?",
                "Search for recipes with onions and peppers",
                "Show me what I can make",
                "Find recipes",
                "Search recipes",
                "Find me something to cook"
            ],
            
            'declare_ingredients': [
                "I have eggs, flour, and milk",
                "I've got tomatoes, cheese, and basil",
                "Available ingredients are chicken, rice, and peas",
                "I have butter and sugar",
                "My ingredients are potatoes, onions, and carrots",
                "I've got olive oil, garlic, and pasta",
                "I have some apples and cinnamon",
                "The ingredients I have are beef, carrots, and potatoes",
                "I've got flour, sugar, and eggs",
                "My available ingredients are spinach and feta",
                "I have ground beef and taco shells",
                "I've got chocolate and butter",
                "I have lemons and sugar"
            ],
            
            'get_recipe_details': [
                "Show me that recipe",
                "Tell me more about this recipe",
                "How do I make this?",
                "What are the instructions?",
                "Tell me how to make it",
                "Give me the details of the recipe",
                "Show me the ingredients and steps",
                "How do I prepare this dish?",
                "What's in this recipe?",
                "Can you show me the full recipe?",
                "Tell me about the recipe",
                "What are the steps for this recipe?",
                "Show me the directions",
                "I want to see the recipe",
                "Recipe details please",
                "Show recipe",
                "How to make it"
            ],
            
            'request_substitution': [
                "I don't have butter",
                "What can I use instead of milk?",
                "Substitute for eggs?",
                "I'm out of flour, what can I use?",
                "What's a good replacement for sugar?",
                "I don't have any garlic",
                "What can replace olive oil?",
                "I need an alternative to sour cream",
                "What can I use if I don't have baking powder?",
                "Substitute for beef?",
                "I ran out of vanilla extract",
                "What can I use instead of breadcrumbs?",
                "I don't have any yeast",
                "Alternative to maple syrup?",
                "I need a substitute for honey"
            ],
            
            'next_step': [
                "What's next?",
                "Next step",
                "What do I do now?",
                "Continue",
                "What's the next instruction?",
                "Next",
                "What follows?",
                "Tell me the next step",
                "Continue with the recipe",
                "What's next in the process?",
                "Show me the next step",
                "Proceed",
                "What comes after this?",
                "Go on",
                "Move to the next step"
            ],
            
            'previous_step': [
                "What was the previous step?",
                "Go back",
                "Repeat that",
                "What was that again?",
                "Previous instruction",
                "Back",
                "Let's go back",
                "What was before this?",
                "Go to the previous step",
                "Can you repeat the last step?",
                "What did you say before?",
                "Go back one step",
                "Show the previous instruction"
            ],
            
            'affirm': [
                "Yes",
                "Yeah",
                "Sure",
                "OK",
                "Sounds good",
                "That works",
                "Correct",
                "Exactly",
                "Right",
                "Yep",
                "Indeed",
                "Absolutely",
                "Fine by me",
                "That's right",
                "Yes please",
                "Of course"
            ],
            
            'deny': [
                "No",
                "Nope",
                "No way",
                "Not really",
                "I don't think so",
                "Negative",
                "Not at all",
                "No thanks",
                "Definitely not",
                "Not interested",
                "I'd rather not",
                "Not now",
                "I don't want that"
            ],
            
            'request_help': [
                "Help",
                "Help me",
                "How does this work?",
                "What can you do?",
                "Show me the commands",
                "I'm confused",
                "I need assistance",
                "What are my options?",
                "How do I use this?",
                "What should I do?",
                "Guide me",
                "What commands can I use?",
                "How do I get started?",
                "What features are available?"
            ],
            
            'greeting': [
                "Hello",
                "Hi",
                "Hey",
                "Good morning",
                "Good afternoon",
                "Good evening",
                "Howdy",
                "Hi there",
                "Greetings",
                "Hello there",
                "Hey there"
            ]
        }
        
        # Path to store/load embeddings
        self.data_dir = self._get_data_dir()
        self.model_path = os.path.join(self.data_dir, 'intent_classifier_model.pkl')
        
        # Create or load intent embeddings
        self.intent_embeddings = {}
        self.intents = list(self.intent_examples.keys())
        
        if os.path.exists(self.model_path):
            self._load_model()
        else:
            self._create_embeddings()
            self._save_model()
    
    def _get_data_dir(self):
        """Get the data directory for storing the model"""
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the project root
        project_dir = os.path.dirname(current_dir)
        # Path to the processed data directory
        return os.path.join(project_dir, 'data', 'processed')
    
    def _create_embeddings(self):
        """Create embeddings for all intent examples"""
        if self.model is None:
            print("Cannot create embeddings: model not loaded")
            return
        
        print("Creating intent embeddings...")
        all_examples = []
        all_intents = []
        
        # Gather all examples and their corresponding intents
        for intent, examples in self.intent_examples.items():
            all_examples.extend(examples)
            all_intents.extend([intent] * len(examples))
        
        # Create embeddings for all examples
        example_embeddings = self.model.encode(all_examples)
        
        # Group embeddings by intent
        self.intent_embeddings = {}
        for intent in self.intents:
            # Get indices of examples for this intent
            indices = [i for i, x in enumerate(all_intents) if x == intent]
            # Get embeddings for these examples
            intent_embs = [example_embeddings[i] for i in indices]
            # Store embeddings for this intent
            self.intent_embeddings[intent] = intent_embs
        
        print(f"Created embeddings for {len(self.intents)} intents")
    
    def _save_model(self):
        """Save the intent classifier model"""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.intent_embeddings, f)
        print(f"Saved intent classifier model to {self.model_path}")
    
    def _load_model(self):
        """Load the intent classifier model"""
        try:
            with open(self.model_path, 'rb') as f:
                self.intent_embeddings = pickle.load(f)
            print(f"Loaded intent classifier model from {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self._create_embeddings()
            self._save_model()
    
    def classify(self, text):
        """
        Classify user input text into an intent
        
        Args:
            text: User input text
            
        Returns:
            dict: Intent classification with confidence score
        """
        if not text or self.model is None:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': {}
            }
        
        # Create embedding for input text
        try:
            text_embedding = self.model.encode([text])[0]
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': {}
            }
        
        # Calculate similarity to all intent examples
        intent_scores = {}
        for intent, embeddings in self.intent_embeddings.items():
            # Calculate cosine similarity with each example
            similarities = [
                cosine_similarity([text_embedding], [emb])[0][0]
                for emb in embeddings
            ]
            # Use max similarity as the score for this intent
            intent_scores[intent] = max(similarities) if similarities else 0.0
        
        # Find the intent with the highest similarity score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_name, confidence = best_intent
        
        # Only classify if confidence is above threshold
        if confidence < 0.55:  # Adjust threshold as needed
            return {
                'intent': 'unknown',
                'confidence': confidence,
                'entities': {}
            }
        
        # Extract entities using pattern-based approach
        # This is simplified entity extraction - in a real system, you'd use a more robust approach
        entities = {}
        
        # For demonstration, we'll extract ingredients from 'search_by_ingredients' or 'declare_ingredients'
        if intent_name in ['search_by_ingredients', 'declare_ingredients']:
            # Simple ingredient extraction by looking for words after "with" or "have"
            text_lower = text.lower()
            ingredients = []
            
            if 'with' in text_lower:
                ingredients_text = text_lower.split('with', 1)[1].strip()
                ingredients = [ing.strip() for ing in ingredients_text.split(',')]
                # Handle "and" in the last item
                if ingredients and ' and ' in ingredients[-1]:
                    last_items = ingredients[-1].split(' and ')
                    ingredients = ingredients[:-1] + [item.strip() for item in last_items]
            elif 'have' in text_lower:
                ingredients_text = text_lower.split('have', 1)[1].strip()
                ingredients = [ing.strip() for ing in ingredients_text.split(',')]
                # Handle "and" in the last item
                if ingredients and ' and ' in ingredients[-1]:
                    last_items = ingredients[-1].split(' and ')
                    ingredients = ingredients[:-1] + [item.strip() for item in last_items]
            
            if ingredients:
                entities['ingredients'] = ingredients
        
        return {
            'intent': intent_name,
            'confidence': confidence,
            'entities': entities
        }
    
    def retrain(self, new_examples=None):
        """
        Retrain the model with new examples
        
        Args:
            new_examples: Dict of intent -> list of new examples
        """
        if new_examples:
            # Add new examples to existing ones
            for intent, examples in new_examples.items():
                if intent in self.intent_examples:
                    self.intent_examples[intent].extend(examples)
                else:
                    self.intent_examples[intent] = examples
            
            # Update intents list
            self.intents = list(self.intent_examples.keys())
        
        # Recreate embeddings and save
        self._create_embeddings()
        self._save_model()

# Test the classifier if run directly
if __name__ == "__main__":
    classifier = DeepLearningIntentClassifier()
    
    # Test examples
    test_inputs = [
        "What can I make with eggs, flour, and milk?",
        "I have cheese, tomatoes, and basil",
        "Show me that recipe",
        "I don't have butter, what can I use instead?",
        "What's the next step?",
        "How much flour do I need?",
        "Help me",
        "Yes",
        "No",
        "Search recipes",
        "Hello",
        "I'd like to find a recipe for chicken"
    ]
    
    print("\nTesting deep learning intent classification:")
    for input_text in test_inputs:
        result = classifier.classify(input_text)
        print(f"\nInput: {input_text}")
        print(f"Intent: {result['intent']} (confidence: {result['confidence']:.4f})")
        if result['entities']:
            print("Entities:", result['entities'])


class IntentClassifier:
    """
    Classifies user intents related to cooking and recipe queries
    Uses pattern matching for the prototype version
    """
    
    def __init__(self):
        """Initialize the intent classifier with patterns"""
        # Define core intents with their patterns
        self.intent_patterns = {
            # Searching for recipes
            'search_by_ingredients': [
                r'what can i (make|cook) with (.*)',
                r'recipes? (using|with) (.*)',
                r'what recipes? (do you have|are available|can i make) (using|with) (.*)',
                r'i have (.*) what can i (make|cook)',
                r'suggest (something|a recipe|recipes) (using|with) (.*)',
                r'show me recipes? (using|with) (.*)',
                r'search for recipes',
                r'find recipes',
                r'show me recipes',
                r'search recipes',
                r'find something to (make|cook)',
                r'search',
                r'find recipe',
                r'recipe search'
            ],
            
            # User declares available ingredients
            'declare_ingredients': [
                r'i have (.*)',
                r'ingredients? i have:? (.*)',
                r'available ingredients?:? (.*)',
                r'i\'ve got (.*)',
                r'i got (.*)',
                r'my ingredients are (.*)',
                r'i (can|could) use (.*)'
            ],
            
            # Getting recipe details
            'get_recipe_details': [
                r'show me (that|this|the) recipe',
                r'(tell me more|details) about (that|this|the) recipe',
                r'how (do|can) i (make|prepare) (it|that|this)',
                r'what are the (steps|instructions)',
                r'tell me how to make (it|that|this)',
                r'show recipe',
                r'recipe details',
                r'full recipe',
                r'ingredients list',
                r'cooking instructions',
                r'how to make it'
            ],
            
            # Request for substitution
            'request_substitution': [
                r'i (don\'?t have|am out of|ran out of) (.*)',
                r'what (can|could) i (use|substitute) (for|instead of) (.*)',
                r'alternative[s]? (to|for) (.*)',
                r'replace (.*) with what',
                r'substitute for (.*)',
                r'what (can|could) replace (.*)',
                r'i need a substitute for (.*)',
                r'don\'?t have (.*)',
                r'missing (.*)',
                r'no (.*) (available|on hand)'
            ],
            
            # Navigation through recipe steps
            'next_step': [
                r'(what\'?s|what is) (the|) next( step)?',
                r'(continue|proceed|go on)',
                r'and then( what)?',
                r'what (do|should) i do next',
                r'next (step|instruction)',
                r'next',
                r'continue',
                r'go on',
                r'proceed',
                r'then what',
                r'now what',
                r'step',
                r'what\'s next'
            ],
            
            'previous_step': [
                r'(what was|what\'?s|what is) the (previous|last)( step)?',
                r'(go|let\'?s go) back',
                r'repeat (that|the step|the instruction)',
                r'what was (that|it) again',
                r'back',
                r'previous',
                r'earlier step',
                r'go back',
                r'repeat',
                r'again'
            ],
            
            # Confirmation of ingredient
            'confirm_ingredient': [
                r'(yes|yeah|yep|sure|ok|okay|of course), i have (.*)',
                r'i have (.*) too',
                r'i (do|can) (use|have) (.*)',
                r'i\'?ve got (.*)',
                r'yes, i (have|\'ve got) (.*)',
                r'i do have (.*)'
            ],
            
            # Affirmation (yes)
            'affirm': [
                r'^(yes|yeah|yep|sure|ok|okay|of course|absolutely|definitely|certainly|right|correct)$',
                r'^y$',
                r'^(sounds?|looks?) good$',
                r'^(that\'?s|that is) (good|great|fine|correct)$',
                r'^(please|pls) do$',
                r'^(go|let\'?s|lets) (ahead|do (it|that))$',
                r'^(i|we) (would|\'?d) like (that|to)$'
            ],
            
            # Negation (no)
            'deny': [
                r'^(no|nope|nah|not|negative|never)$',
                r'^n$',
                r'^(i|we) (don\'?t|do not) (want|need) (that|to|it)$',
                r'^(that\'?s|that is) (not|isn\'?t) (good|what i want|right|correct)$',
                r'^(please|pls) (don\'?t|do not)$',
                r'^(i|we) (would|\'?d) (not|rather not)$'
            ],
            
            # Ingredient quantity questions
            'ask_ingredient_quantity': [
                r'how much (.*) (do i need|is needed|should i use)',
                r'how many (.*) (do i need|are needed|should i use)',
                r'quantity of (.*)',
                r'amount of (.*) (needed|required)',
                r'how much (.*)',
                r'how many (.*)',
                r'quantity (.*)',
                r'amount (.*)'
            ],
            
            # Dietary restrictions or preferences
            'express_dietary_restriction': [
                r'i (can\'?t eat|don\'?t eat|am allergic to) (.*)',
                r'i am (vegetarian|vegan|gluten.free|dairy.free)',
                r'i have (a|an) (.*) allergy',
                r'no (.*) please',
                r'allergic to (.*)',
                r'can\'?t have (.*)',
                r'dietary restriction: (.*)',
                r'dietary preference: (.*)'
            ],
            
            # General help request
            'request_help': [
                r'(help|assist) me',
                r'how (does this work|do you work)',
                r'what can you do',
                r'(show|tell) me the commands',
                r'i\'?m (confused|lost)',
                r'help',
                r'instructions',
                r'guide',
                r'how to use',
                r'commands',
                r'options',
                r'features',
                r'capabilities'
            ],
            
            # Recipe completion
            'recipe_completed': [
                r'(done|finished|complete|ready|made it)',
                r'i (have|\'?ve) finished (cooking|making|preparing) (it|this|that)',
                r'recipe (completed|done|finished)',
                r'all (done|finished|complete|ready)',
                r'finished',
                r'completed',
                r'made it',
                r'it\'?s done',
                r'it\'?s ready'
            ],
            
            # Recipe feedback
            'recipe_feedback': [
                r'(it was|that was) (delicious|good|great|awesome|terrible|bad|awful)',
                r'i (liked|loved|enjoyed|didn\'?t like|hated) (it|that|this)',
                r'(great|good|bad|terrible) recipe',
                r'delicious',
                r'tasty',
                r'yummy',
                r'disgusting',
                r'awful',
                r'terrible',
                r'great',
                r'good',
                r'bad',
                r'loved it',
                r'hated it'
            ],
            
            # Greeting
            'greeting': [
                r'^(hello|hi|hey|howdy|hiya|good (morning|afternoon|evening)|greetings)$',
                r'^(hello|hi|hey|howdy|hiya) there$',
                r'^(what\'?s up|sup)$'
            ]
        }
        
        # Compile the patterns for efficiency
        self.compiled_patterns = {}
        for intent, patterns in self.intent_patterns.items():
            self.compiled_patterns[intent] = [re.compile(f"^{pattern}$", re.IGNORECASE) for pattern in patterns]
    
    def classify(self, text):
        """
        Classify the user's input into an intent
        
        Args:
            text: User input text
            
        Returns:
            dict: Intent classification with entities
        """
        # Clean the text (remove excess whitespace, etc.)
        clean_text = self._clean_text(text)
        
        # Special case for empty/very short input
        if not clean_text or len(clean_text) < 2:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': {}
            }
        
        # First, check for exact matches (especially for short inputs like "yes", "no")
        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.match(clean_text):
                    # Extract entities based on intent
                    entities = self._extract_entities(intent, pattern.match(clean_text), clean_text)
                    return {
                        'intent': intent,
                        'confidence': 1.0,
                        'entities': entities
                    }
        
        # If no exact match, try partial matching for longer inputs
        for intent, patterns in self.intent_patterns.items():
            for pattern_str in patterns:
                # Remove the start/end anchors for partial matching
                search_pattern = pattern_str.lstrip('^').rstrip('$')
                pattern = re.compile(search_pattern, re.IGNORECASE)
                match = pattern.search(clean_text)
                if match:
                    # Extract entities based on intent
                    entities = self._extract_entities(intent, match, clean_text)
                    return {
                        'intent': intent,
                        'confidence': 0.8,  # Lower confidence for partial matching
                        'entities': entities
                    }
        
        # No intent matched, check if it's general ingredient discussion
        if self._contains_ingredients(clean_text):
            return {
                'intent': 'discuss_ingredient',
                'confidence': 0.7,
                'entities': self._extract_ingredients(clean_text)
            }
        
        # Default to unknown intent
        return {
            'intent': 'unknown',
            'confidence': 0.0,
            'entities': {}
        }
    
    def _clean_text(self, text):
        """Clean and normalize text for better matching"""
        # Remove excess whitespace
        text = ' '.join(text.split())
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation from ends of words but keep internal punctuation
        words = text.split()
        cleaned_words = []
        for word in words:
            word = word.strip(string.punctuation)
            cleaned_words.append(word)
        
        return ' '.join(cleaned_words)
    
    def _contains_ingredients(self, text):
        """Check if the text contains common ingredient-related terms"""
        ingredient_terms = ['flour', 'sugar', 'salt', 'butter', 'oil', 'water', 'egg', 
                           'milk', 'cheese', 'meat', 'chicken', 'beef', 'pork', 'fish',
                           'vegetable', 'fruit', 'spice', 'herb', 'onion', 'garlic',
                           'pepper', 'tomato', 'potato', 'rice', 'pasta', 'bread']
        
        for term in ingredient_terms:
            if re.search(r'\b' + term + r'\b', text, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_ingredients(self, text):
        """Extract potential ingredients from text"""
        # This is a simple implementation for the prototype
        # A more robust implementation would use NER or a comprehensive ingredient database
        
        # Try to find comma or 'and' separated ingredients
        ingredients = []
        
        # Split by common separators
        for segment in re.split(r',|\band\b', text):
            segment = segment.strip()
            if segment and not segment.startswith('i have') and not segment.startswith('i\'ve got'):
                ingredients.append(segment)
        
        return {'ingredients': ingredients}
    
    def _extract_entities(self, intent, match, text):
        """
        Extract entities based on the recognized intent and regex match
        
        Args:
            intent: The recognized intent
            match: The regex match object
            text: The original cleaned text
            
        Returns:
            dict: Extracted entities
        """
        entities = {}
        
        if intent == 'search_by_ingredients' or intent == 'declare_ingredients':
            # Extract ingredients
            if match and match.groups() and len(match.groups()) > 0:
                ingredients_text = match.groups()[-1]  # Take the last capture group
                ingredients = []
                
                # Split by common separators and clean
                for segment in re.split(r',|\band\b', ingredients_text):
                    segment = segment.strip()
                    if segment:
                        ingredients.append(segment)
                
                entities['ingredients'] = ingredients
        
        elif intent == 'request_substitution':
            # Extract the ingredient to substitute
            if match and match.groups() and len(match.groups()) > 0:
                ingredient = match.groups()[-1]  # Take the last capture group
                entities['ingredient'] = ingredient.strip()
        
        elif intent == 'confirm_ingredient':
            # Extract the confirmed ingredient
            if match and match.groups() and len(match.groups()) > 0:
                ingredient = match.groups()[-1]  # Take the last capture group
                entities['ingredient'] = ingredient.strip()
        
        elif intent == 'ask_ingredient_quantity':
            # Extract the ingredient being asked about
            if match and match.groups() and len(match.groups()) > 0:
                ingredient = match.groups()[0]  # First capture should be the ingredient
                entities['ingredient'] = ingredient.strip()
        
        elif intent == 'express_dietary_restriction':
            # Extract the dietary restriction
            if match and match.groups() and len(match.groups()) > 0:
                restriction = match.groups()[-1]  # Last capture should be the restriction
                entities['restriction'] = restriction.strip()
        
        return entities
    
    def add_custom_intent(self, intent_name, patterns):
        """
        Add a custom intent with patterns
        
        Args:
            intent_name: Name of the new intent
            patterns: List of regex patterns for the intent
        """
        if intent_name not in self.intent_patterns:
            self.intent_patterns[intent_name] = patterns
            self.compiled_patterns[intent_name] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def get_example_phrases(self, intent):
        """
        Get example phrases for a specific intent
        
        Args:
            intent: The intent to get examples for
            
        Returns:
            list: Example phrases for the intent
        """
        examples = {
            'search_by_ingredients': [
                "What can I make with eggs and flour?",
                "Show me recipes with chicken and rice",
                "I have tomatoes, cheese, and basil, what can I cook?"
            ],
            'declare_ingredients': [
                "I have butter, sugar, and eggs",
                "Ingredients I have: milk, flour, chocolate",
                "Available ingredients: potatoes, onions, garlic"
            ],
            'request_substitution': [
                "I don't have butter",
                "What can I use instead of milk?",
                "Substitute for eggs?"
            ],
            'next_step': [
                "What's next?",
                "Next step",
                "What do I do now?"
            ],
            'get_recipe_details': [
                "Show me that recipe",
                "How do I make this?",
                "What are the instructions?"
            ],
            'affirm': [
                "Yes",
                "Sure",
                "That sounds good"
            ],
            'deny': [
                "No",
                "I don't want that",
                "Not what I'm looking for"
            ]
        }
        
        return examples.get(intent, ["No examples available for this intent"])

# # Test the intent classifier if run directly
# if __name__ == "__main__":
#     classifier = IntentClassifier()
    
#     # Test examples
#     test_inputs = [
#         "What can I make with eggs, flour, and milk?",
#         "I have cheese, tomatoes, and basil",
#         "Show me that recipe",
#         "I don't have butter, what can I use instead?",
#         "What's the next step?",
#         "How much flour do I need?",
#         "I'm allergic to nuts",
#         "Help me",
#         "I've finished cooking",
#         "That was delicious!",
#         "Can I add garlic to this?",
#         "yes",
#         "no",
#         "search",
#         "show me recipes",
#         "hello",
#         "next"
#     ]
    
#     print("Testing intent classification:")
#     for input_text in test_inputs:
#         result = classifier.classify(input_text)
#         print(f"\nInput: {input_text}")
#         print(f"Intent: {result['intent']} (confidence: {result['confidence']})")
#         if result['entities']:
#             print("Entities:", result['entities'])