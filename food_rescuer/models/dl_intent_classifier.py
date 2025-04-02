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
            ],

            'select_recipe': [
                "I want recipe 1",
                "Show me recipe 2",
                "Let's try recipe 3",
                "Recipe number 2 please",
                "I'll take the first one",
                "The second recipe looks good",
                "I want to try the chicken recipe",
                "Let's make the pasta dish",
                "I'll go with the soup",
                "Show me the first option",
                "Option 3 please",
                "Number 2 looks good",
                "The chocolate cake recipe",
                "I want to make the pizza",
                "I choose the salad recipe"
            ],

            'show_more_recipes': [
                "Show me more recipes",
                "What else can I make?",
                "Are there other options?",
                "Show other recipes",
                "What other recipes do you have?",
                "More recipe options please",
                "Show alternatives",
                "Other suggestions?",
                "What else is possible?",
                "Show me different recipes",
                "Different options",
                "I want to see other recipes",
                "Give me more choices",
                "Are there more recipes?",
                "Show the rest of the recipes"
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

    def extract_entities(text):
        """
        Extract entities from user input using a more sophisticated approach
        
        Args:
            text: User input text
            
        Returns:
            dict: Dictionary of extracted entities
        """
        entities = {}
        
        # Common ingredients list for better recognition
        common_ingredients = [
            # Proteins
            "chicken", "beef", "pork", "tofu", "eggs", "turkey", "salmon", "tuna", "shrimp",
            # Dairy
            "milk", "cream", "butter", "cheese", "yogurt", "sour cream", "cream cheese",
            # Vegetables
            "onion", "garlic", "tomato", "tomatoes", "potato", "potatoes", "carrot", "carrots",
            "broccoli", "spinach", "pepper", "peppers", "cucumber", "lettuce", "celery",
            # Fruits
            "apple", "banana", "orange", "lemon", "lime", "avocado", "strawberry", "strawberries",
            "blueberry", "blueberries", "raspberry", "raspberries", "pineapple", "mango",
            # Grains and starches
            "rice", "pasta", "flour", "bread", "noodles", "quinoa", "oats", "oatmeal",
            # Spices and seasonings
            "salt", "pepper", "oregano", "basil", "thyme", "cinnamon", "cumin", "paprika",
            # Oils and fats
            "olive oil", "vegetable oil", "coconut oil", "sesame oil",
            # Common cooking ingredients
            "sugar", "brown sugar", "honey", "maple syrup", "soy sauce", "vinegar",
            "baking powder", "baking soda", "vanilla", "chocolate", "nuts"
        ]
        
        # Detect ingredients using a more thorough approach
        detected_ingredients = []
        
        # Convert to lowercase for matching
        text_lower = text.lower()
        
        # Check if the text contains phrases indicating ingredient declaration
        ingredients_text = None
        declaration_phrases = [
            "i have ", "i've got ", "i've been using ", "i'm using ", 
            "available ingredients", "ingredients i have", "in my pantry",
            "in my kitchen", "in my fridge", "i can use", "i want to use"
        ]
        
        # Special handling for phrases like "I have X"
        for phrase in declaration_phrases:
            if phrase in text_lower:
                split_point = text_lower.find(phrase) + len(phrase)
                ingredients_text = text_lower[split_point:].strip()
                break
        
        # Special handling for "What can I make with X" type questions
        search_phrases = [
            "what can i make with ", "what can i cook with ", "recipes with ",
            "recipes using ", "dishes with ", "cook with ", "recipes for "
        ]
        
        for phrase in search_phrases:
            if phrase in text_lower:
                split_point = text_lower.find(phrase) + len(phrase)
                ingredients_text = text_lower[split_point:].strip()
                break
        
        # If we found a relevant section, process it
        if ingredients_text:
            # Split by common separators
            for sep in [", ", " and ", "; "]:
                if sep in ingredients_text:
                    items = ingredients_text.split(sep)
                    for item in items:
                        item = item.strip().strip(',.?!')
                        if item:
                            detected_ingredients.append(item)
                    
                    # If we found ingredients with a separator, stop processing
                    if detected_ingredients:
                        break
            
            # If no separators found, treat the whole phrase as a single ingredient or check for known ingredients
            if not detected_ingredients:
                # Clean up the text
                ingredients_text = ingredients_text.strip(',.?!')
                
                # Check if the text matches any of our known ingredients
                for ingredient in common_ingredients:
                    if ingredient in ingredients_text:
                        detected_ingredients.append(ingredient)
                
                # If no known ingredients found, try the whole text
                if not detected_ingredients and ingredients_text:
                    detected_ingredients.append(ingredients_text)
        
        # If no declaration or search phrases found, scan for known ingredients
        if not detected_ingredients:
            for ingredient in common_ingredients:
                if ingredient in text_lower:
                    detected_ingredients.append(ingredient)
        
        # If ingredients were found, add them to the entities
        if detected_ingredients:
            entities['ingredients'] = detected_ingredients
        
        # Extract dietary restrictions or preferences
        dietary_keywords = [
            "vegetarian", "vegan", "gluten-free", "dairy-free", "nut-free",
            "lactose-free", "paleo", "keto", "low-carb", "low-fat"
        ]
        
        detected_restrictions = []
        for restriction in dietary_keywords:
            if restriction in text_lower:
                detected_restrictions.append(restriction)
        
        if detected_restrictions:
            entities['dietary_restrictions'] = detected_restrictions
        
        # Extract cooking techniques if mentioned
        cooking_techniques = [
            "bake", "roast", "fry", "grill", "steam", "boil", "sauté",
            "simmer", "broil", "poach"
        ]
        
        detected_techniques = []
        for technique in cooking_techniques:
            if technique in text_lower:
                detected_techniques.append(technique)
        
        if detected_techniques:
            entities['cooking_techniques'] = detected_techniques
        
        return entities
    



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
            dict: Intent classification with confidence score and entities
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
            intent_name = 'unknown'
        
        # Use the enhanced entity extraction function
        # First, import it at the top of your file
        # from utils.entity_extraction import extract_entities
        
        # For now, use the existing entity extraction as a fallback
        entities = {}
        
        # Extract entities using our improved method
        try:
            # This would be the call to the external function
            # entities = extract_entities(text)
            
            # If the function isn't available yet, use your existing extraction
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
        except Exception as e:
            print(f"Error in entity extraction: {e}")
        
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