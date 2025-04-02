# food_rescuer/utils/entity_extraction.py
# Utility functions for extracting entities from user input

import re
from typing import List, Dict, Any

# Common cooking ingredients for better recognition
COMMON_INGREDIENTS = [
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

def extract_ingredients(text: str) -> List[str]:
    """
    Extract ingredients mentioned in the user's text
    
    Args:
        text: User input text
        
    Returns:
        list: List of extracted ingredient names
    """
    ingredients = []
    
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
    if not ingredients_text:
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
        # First try to split by common separators
        for sep in [", ", " and ", "; "]:
            if sep in ingredients_text:
                items = ingredients_text.split(sep)
                for item in items:
                    item = item.strip().strip(',.?!')
                    if item:
                        ingredients.append(item)
                
                # If we found ingredients with a separator, stop processing
                if ingredients:
                    break
        
        # If no separators found, check for known ingredients in the text
        if not ingredients:
            for ingredient in COMMON_INGREDIENTS:
                if ingredient in ingredients_text:
                    ingredients.append(ingredient)
    
    # If no declaration or search phrases found, scan for known ingredients in the full text
    if not ingredients:
        for ingredient in COMMON_INGREDIENTS:
            if ingredient in text_lower:
                ingredients.append(ingredient)
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(ingredients))

# Add to utils/entity_extraction.py

def extract_recipe_selection(text):
    """
    Extract recipe selection information from user input
    
    Args:
        text: User input text
        
    Returns:
        dict: Dictionary with recipe selection information
    """
    entities = {}
    
    if not text:
        return entities
    
    # Convert to lowercase for matching
    text_lower = text.lower()
    
    # Look for recipe numbers (e.g., "recipe 1", "number 2", "option 3")
    import re
    number_patterns = [
        r'\bnumber\s+(\d+)\b',
        r'\brecipe\s+(\d+)\b',
        r'\boption\s+(\d+)\b',
        r'\b(\d+)(?:st|nd|rd|th)?\b'  # matches "1st", "2nd", "3", etc.
    ]
    
    for pattern in number_patterns:
        match = re.search(pattern, text_lower)
        if match:
            entities['recipe_number'] = match.group(1)
            break
    
    # Look for recipe selection phrases
    selection_phrases = [
    r'choose\s+(?:the\s+)?(.+?)\s+recipe',
    r'select\s+(?:the\s+)?(.+?)\s+recipe',
    r'make\s+(?:the\s+)?(.+?)\s+recipe',
    r'try\s+(?:the\s+)?(.+?)\s+recipe',
    r'let\'s\s+(?:try|make|do)\s+(?:the\s+)?(.+?)\s+recipe',
    r'let\'s\s+(?:try|make|do)\s+(?:the\s+)?(.+?)$',
    r'want\s+(?:to\s+make|to\s+try|the)\s+(.+?)\s+recipe',
    r'show\s+(?:me\s+)?(?:the\s+)?(.+?)\s+recipe'
]

    # How to use these patterns in the extract_recipe_selection function:
    for pattern in selection_phrases:
        match = re.search(pattern, text_lower)
        if match:
            recipe_name = match.group(1).strip()
            # Don't capture very short or generic terms
            if len(recipe_name) > 3 and recipe_name not in ['a', 'an', 'this', 'that', 'the']:
                entities['recipe_name'] = recipe_name
                break
        
    # Look for specific selection phrases like "I want the first one"
    ordinal_patterns = {
        'first': '1',
        'second': '2',
        'third': '3',
        'fourth': '4',
        'fifth': '5',
        'last': 'last'  # Special case, needs to be handled by caller
    }
    
    for ordinal, number in ordinal_patterns.items():
        if f"the {ordinal}" in text_lower or f"{ordinal} one" in text_lower or f"{ordinal} recipe" in text_lower:
            entities['recipe_number'] = number
            break
    
    # Check for direct mentions of the recipe index
    if not 'recipe_number' in entities and not 'recipe_name' in entities:
        # Look for single digits that might be recipe numbers
        digit_match = re.search(r'\b[1-9]\b', text_lower)
        if digit_match:
            entities['recipe_number'] = digit_match.group(0)
    
    return entities

def extract_missing_ingredients(text: str) -> List[str]:
    """
    Extract ingredients that the user mentions they don't have
    
    Args:
        text: User input text
        
    Returns:
        list: List of missing ingredients
    """
    missing = []
    
    # Convert to lowercase for matching
    text_lower = text.lower()
    
    # Check for phrases indicating missing ingredients
    missing_phrases = [
        "i don't have ", "don't have ", "ran out of ", "out of ", 
        "missing ", "no more ", "need ", "substitute for "
    ]
    
    for phrase in missing_phrases:
        if phrase in text_lower:
            # Extract the text after the phrase
            split_point = text_lower.find(phrase) + len(phrase)
            missing_text = text_lower[split_point:].strip()
            
            # Extract the first word or phrase
            match = re.search(r'^([a-z\s]+)', missing_text)
            if match:
                ingredient = match.group(1).strip()
                # Clean up any trailing punctuation
                ingredient = re.sub(r'[.,;!?].*$', '', ingredient)
                if ingredient:
                    missing.append(ingredient)
                    break
    
    # Alternatively, look for known ingredients preceded by "no" or "without"
    if not missing:
        for ingredient in COMMON_INGREDIENTS:
            for prefix in ["no ", "without "]:
                if prefix + ingredient in text_lower:
                    missing.append(ingredient)
    
    return missing

def extract_dietary_restrictions(text: str) -> List[str]:
    """
    Extract any dietary restrictions mentioned in the text
    
    Args:
        text: User input text
        
    Returns:
        list: List of dietary restrictions
    """
    restrictions = []
    
    # Common dietary restrictions
    restriction_terms = [
        "vegetarian", "vegan", "gluten-free", "gluten free", "dairy-free", "dairy free",
        "nut-free", "nut free", "lactose-free", "lactose free", "low-carb", "low carb",
        "keto", "ketogenic", "paleo", "pescatarian", "kosher", "halal"
    ]
    
    # Normalize text
    text_lower = text.lower()
    
    # Check for each restriction
    for restriction in restriction_terms:
        # Look for phrases like "I'm vegetarian" or "vegetarian diet"
        patterns = [
            rf'\b{restriction}\b',  # the word by itself
            rf'i\'m {restriction}',  # "I'm vegetarian"
            rf'i am {restriction}',  # "I am vegetarian"
            rf'{restriction} diet',  # "vegetarian diet"
        ]
        
        for pattern in patterns:
            if re.search(pattern, text_lower):
                # Normalize the restriction (remove "free" and use hyphen)
                if "free" in restriction:
                    base = restriction.replace(" free", "").replace("-free", "")
                    normalized = f"{base}-free"
                else:
                    normalized = restriction
                
                restrictions.append(normalized)
                break
    
    return list(set(restrictions))  # Remove duplicates

# Add this function to utils/entity_extraction.py or your existing entity extraction module

def extract_recipe_selection(text):
    """
    Extract recipe selection information from user input
    
    Args:
        text: User input text
        
    Returns:
        dict: Dictionary with recipe selection information
    """
    entities = {}
    
    # Convert to lowercase for matching
    text_lower = text.lower()
    
    # Look for recipe numbers (e.g., "recipe 1", "number 2", "option 3")
    import re
    number_patterns = [
        r'\bnumber\s+(\d+)\b',
        r'\brecipe\s+(\d+)\b',
        r'\boption\s+(\d+)\b',
        r'\b(\d+)(?:st|nd|rd|th)?\b'  # matches "1st", "2nd", "3", etc.
    ]
    
    for pattern in number_patterns:
        match = re.search(pattern, text_lower)
        if match:
            entities['recipe_number'] = match.group(1)
            break
    
    # Look for specific selection phrases like "I want the first one"
    ordinal_patterns = {
        'first': '1',
        'second': '2',
        'third': '3',
        'fourth': '4',
        'fifth': '5',
        'last': 'last'  # Special case, needs to be handled by caller
    }
    
    for ordinal, number in ordinal_patterns.items():
        if f"the {ordinal}" in text_lower or f"{ordinal} one" in text_lower or f"{ordinal} recipe" in text_lower:
            entities['recipe_number'] = number
            break
    
    # Look for recipe names in the text
    # This would need to be matched against actual recipe names by the caller
    
    return entities

def extract_entities(text: str) -> Dict[str, Any]:
    """
    Extract all relevant entities from user input
    
    Args:
        text: User input text
        
    Returns:
        dict: Dictionary of extracted entities
    """
    entities = {}
    
    # Extract available ingredients
    ingredients = extract_ingredients(text)
    if ingredients:
        entities['ingredients'] = ingredients
    
    # Extract missing ingredients
    missing = extract_missing_ingredients(text)
    if missing:
        entities['missing_ingredients'] = missing
    
    # Extract dietary restrictions
    restrictions = extract_dietary_restrictions(text)
    if restrictions:
        entities['dietary_restrictions'] = restrictions
    
    return entities