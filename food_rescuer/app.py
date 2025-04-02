# food_rescuer/app.py
# Main application file for Food Rescuer

import os
import sys
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation.state_manager import ConversationManager
from data.food_substitutions import SubstitutionKnowledgeBase
from models.recipe_retrieval import RecipeRetriever
from models.intent_classifier import IntentClassifier

def initialize_assistant():
    """Initialize the Food Rescuer assistant components"""
    print("Initializing Food Rescuer assistant...")
    
    # Check if data exists
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "processed")
    recipes_path = os.path.join(data_dir, "processed_recipes.json")
    
    if not os.path.exists(recipes_path):
        print("Error: Processed recipes not found!")
        print(f"Please run the data processing script to generate {recipes_path}")
        return None
    
    # Load substitution knowledge base
    print("Loading ingredient substitutions...")
    substitution_kb = SubstitutionKnowledgeBase()
    
    # Initialize recipe retriever
    print("Loading recipe database...")
    recipe_retriever = RecipeRetriever()
    
    # Initialize intent classifier
    print("Setting up intent recognition...")
    intent_classifier = IntentClassifier()
    
    # Create the conversation manager
    conversation_manager = ConversationManager(
        substitution_kb=substitution_kb,
        recipe_retriever=recipe_retriever,
        intent_classifier=intent_classifier
    )
    
    print("Food Rescuer assistant initialized successfully!")
    return conversation_manager

def print_welcome_message():
    """Print a welcome message for the Food Rescuer assistant"""
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

def print_thinking_animation(duration=1.0):
    """Display a simple thinking animation"""
    frames = ["Thinking.", "Thinking..", "Thinking..."]
    end_time = time.time() + duration
    
    i = 0
    while time.time() < end_time:
        print(f"\r{frames[i % len(frames)]}", end="", flush=True)
        time.sleep(0.3)
        i += 1
    
    print("\r" + " " * 20 + "\r", end="", flush=True)

def run_interactive_session(conversation_manager):
    """Run an interactive session with the Food Rescuer assistant"""
    print_welcome_message()
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using Food Rescuer. Goodbye!")
            break
        
        print_thinking_animation(0.7)
        
        response = conversation_manager.process(user_input)
        print(f"\nFood Rescuer: {response}")

def main():
    """Main function to run the Food Rescuer application"""
    conversation_manager = initialize_assistant()
    
    if conversation_manager:
        run_interactive_session(conversation_manager)

if __name__ == "__main__":
    main()