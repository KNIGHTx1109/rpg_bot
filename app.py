import streamlit as st
import database
import game_manager

st.set_page_config(page_title="AI RPG Bot", layout="wide")

# Initialize DB on start
if "db_initialized" not in st.session_state:
    database.init_db()
    st.session_state.db_initialized = True

st.title("🗡️ AI Dungeon Master - RPG Bot")

# Sidebar for Stats
with st.sidebar:
    st.header("Player Stats")
    state = database.get_player_state()
    if state:
        st.metric("Health", f"{state['health']} / 100")
        st.write(f"**Location:** {state['location']}")
        st.write("**Inventory:**")
        if state['inventory']:
            for item in state['inventory']:
                st.write(f"- {item}")
        else:
            st.write("*(Empty)*")
            
    if st.button("Restart Game"):
        game_manager.start_new_game()
        st.rerun()

# Chat interface
history = database.get_chat_history()
if not history:
    # First load
    intro = game_manager.start_new_game()
    history = [{"role": "assistant", "content": intro}]

# Display chat messages
for msg in history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("What do you do?"):
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.spinner("The DM is thinking..."):
        try:
            result = game_manager.process_turn(prompt)
            with st.chat_message("assistant"):
                st.markdown(result["narrative"])
                
            if result["is_game_over"]:
                st.error("Game Over! Please restart.")
            else:
                st.rerun()
        except Exception as e:
            st.error(f"Error communicating with LLM: {e}")
