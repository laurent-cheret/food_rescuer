# food_rescuer/update_to_dl.py
# Script to update the Food Rescuer app to use the deep learning intent classifier

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation.state_manager import ConversationManager
from data.food_substitutions import SubstitutionKnowledgeBase
from models.recipe_retrieval import RecipeRetriever
from models.dl_intent_classifier import DeepLearningIntentClassifier

def update_assistant():
    """Update the Food Rescuer assistant with the deep learning intent classifier"""
    print("Updating Food Rescuer to use deep learning intent classification...")
    
    # Check if data exists
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "processed")
    recipes_path = os.path.join(data_dir, "processed_recipes.json")
    
    if not os.path.exists(recipes_path):
        print("Error: Processed recipes not found!")
        print(f"Please run the data processing script to generate {recipes_path}")
        return None
    
    # Initialize components
    print("Loading ingredient substitutions...")
    substitution_kb = SubstitutionKnowledgeBase()
    
    print("Loading recipe database...")
    recipe_retriever = RecipeRetriever()
    
    print("Setting up deep learning intent classifier...")
    intent_classifier = DeepLearningIntentClassifier()
    
    # Create the conversation manager with the deep learning intent classifier
    conversation_manager = ConversationManager(
        substitution_kb=substitution_kb,
        recipe_retriever=recipe_retriever,
        intent_classifier=intent_classifier
    )
    
    print("Food Rescuer successfully updated to use deep learning intent classification!")
    return conversation_manager

def run_interactive_session(conversation_manager):
    """Run an interactive session with the updated Food Rescuer assistant"""
    print("\n" + "=" * 60)
    print(" 🥕 FOOD RESCUER 🍳 ".center(60))
    print(" Cook better with what you have ".center(60))
    print("=" * 60)
    print("\nWelcome to Food Rescuer!")
    print("I'll help you find recipes using ingredients you already have,")
    print("and suggest substitutions when you're missing something.")
    print("\nGet started by telling me what ingredients you have available,")
    print("or ask for help to learn more about what I can do.")
    print("\nType 'exit' at any time to quit.")
    print("-" * 60)
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using Food Rescuer. Goodbye!")
            break
        
        # Print a thinking message
        print("Thinking...", end="\r")
        
        response = conversation_manager.process(user_input)
        print(f"\nFood Rescuer: {response}")

def main():
    """Main function to update and run the Food Rescuer application"""
    conversation_manager = update_assistant()
    
    if conversation_manager:
        run_interactive_session(conversation_manager)

if __name__ == "__main__":
    main()