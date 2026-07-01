import database
import llm_engine

def process_turn(user_action: str):
    # 1. Get state
    state = database.get_player_state()
    history = database.get_chat_history()
    
    # 2. Get LLM response
    response_json = llm_engine.generate_response(user_action, state, history)
    
    # 3. Parse updates
    narrative = response_json.get("narrative", "...")
    health_change = response_json.get("health_change", 0)
    new_location = response_json.get("new_location")
    inv_added = response_json.get("inventory_added", [])
    inv_removed = response_json.get("inventory_removed", [])
    is_game_over = response_json.get("is_game_over", False)
    
    # 4. Apply updates to state
    new_health = min(100, max(0, state["health"] + health_change))
    location = new_location if new_location else state["location"]
    
    inventory = state["inventory"]
    for item in inv_removed:
        if item in inventory:
            inventory.remove(item)
    for item in inv_added:
        inventory.append(item)
        
    if new_health <= 0:
        is_game_over = True
        narrative += "\n\n**You have died. Game Over.**"
        
    # 5. Save to database
    database.update_player_state(new_health, location, inventory)
    database.add_chat_message("user", user_action)
    database.add_chat_message("assistant", narrative)
    
    return {
        "narrative": narrative,
        "state": {
            "health": new_health,
            "location": location,
            "inventory": inventory
        },
        "is_game_over": is_game_over
    }

def start_new_game():
    database.init_db()
    database.reset_game()
    initial_prompt = "You wake up in a dimly lit tavern. You have nothing but the clothes on your back. The bartender is staring at you."
    database.add_chat_message("assistant", initial_prompt)
    return initial_prompt
