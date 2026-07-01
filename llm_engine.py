import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# We will initialize the client when needed to ensure the env var is loaded.
def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in a .env file.")
    return Groq(api_key=api_key)

SYSTEM_PROMPT = """
You are a Dungeon Master for an interactive text-based adventure RPG.
You must output ONLY valid JSON.
The current game state will be provided to you. Based on the user's input, you must advance the narrative, and update the player's state.
Your response MUST be a JSON object with the following schema:
{
    "narrative": "The story text describing what happens next, presented to the player.",
    "health_change": integer (positive for healing, negative for damage, 0 for no change),
    "new_location": "String of the new location, or null if it didn't change",
    "inventory_added": ["item1", "item2"] (or empty list),
    "inventory_removed": ["item1"] (or empty list),
    "is_game_over": boolean
}
Keep the narrative engaging and descriptive.
"""

def generate_response(user_input: str, current_state: dict, chat_history: list):
    client = get_client()
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    
    # Add context history
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    # Build the user message with current state and action
    state_str = json.dumps(current_state, indent=2)
    user_message = f"Current State:\n{state_str}\n\nPlayer Action: {user_input}"
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b", 
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.7,
        max_tokens=1024
    )
    
    result_str = response.choices[0].message.content
    try:
        return json.loads(result_str)
    except json.JSONDecodeError:
        return {
            "narrative": "An error occurred parsing the DM's response. Please try again.",
            "health_change": 0,
            "new_location": None,
            "inventory_added": [],
            "inventory_removed": [],
            "is_game_over": False
        }
