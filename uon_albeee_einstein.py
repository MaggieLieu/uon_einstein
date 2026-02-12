import streamlit as st
import os
from adk_service import initialize_adk, run_adk_sync
from settings import MESSAGE_HISTORY_KEY


if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
# Option 2: From environment variable (already set)
elif "GOOGLE_API_KEY" not in os.environ:
    # Option 3: Prompt user to enter it
    st.error("⚠️ Google API Key not found!")
    api_key = st.text_input("Enter your Google API Key:", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        st.rerun()
    else:
        st.stop()


# Page configuration
st.set_page_config(
    page_title="Albeee Einstein - UoN Physics Assistant",
    page_icon="🔬",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        max-width: 800px;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔬 Albeee Einstein")
st.caption("Your University of Nottingham Physics & Astronomy Ambassador")


adk_runner, current_session_id = initialize_adk()

st.subheader("Chat with the Assistant") # Subheading for the chat section.
# Initialize chat message history in Streamlit's session state if it doesn't exist.
if MESSAGE_HISTORY_KEY not in st.session_state:
    st.session_state[MESSAGE_HISTORY_KEY] = []
# Display existing chat messages from the session state.
for message in st.session_state[MESSAGE_HISTORY_KEY]:
    with st.chat_message(message["role"]): # Use Streamlit's chat message container for styling.
        st.markdown(message["content"])
# Handle new user input.
if prompt := st.chat_input("Ask for a greeting (e.g., 'greet me'), or just chat..."):
    # Append user's message to history and display it.
    st.session_state[MESSAGE_HISTORY_KEY].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # Process the user's message with the ADK agent and display the response.
    with st.chat_message("assistant"):
        message_placeholder = st.empty() # Create an empty placeholder to update with the assistant's response.
        with st.spinner("Assistant is thinking..."): # Show a spinner while the agent processes the request.
            agent_response = run_adk_sync(adk_runner, current_session_id, prompt) # Call the synchronous ADK runner.
            message_placeholder.markdown(agent_response) # Update the placeholder with the final response.
    
    # Append assistant's response to history.
    st.session_state[MESSAGE_HISTORY_KEY].append({"role": "assistant", "content": agent_response})
