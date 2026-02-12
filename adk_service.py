import streamlit as st
import asyncio
import time
import os
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types
from greeting_agent import create_greeting_agent
from settings import APP_NAME_FOR_ADK, USER_ID, INITIAL_STATE, ADK_SESSION_KEY
@st.cache_resource
def initialize_adk():
    root_agent = create_greeting_agent()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME_FOR_ADK,
        session_service=session_service
    )

    if ADK_SESSION_KEY not in st.session_state:
        session_id = f"streamlit_adk_session_{int(time.time())}_{os.urandom(4).hex()}"
        st.session_state[ADK_SESSION_KEY] = session_id
        
        # FIX: Use asyncio.run to ensure the session is actually created before continuing
        asyncio.run(session_service.create_session(
            app_name=APP_NAME_FOR_ADK,
            user_id=USER_ID,
            session_id=session_id,
            state=INITIAL_STATE,
        ))
    else:
        session_id = st.session_state[ADK_SESSION_KEY]
        # FIX: Use asyncio.run for the existence check
        existing_session = asyncio.run(session_service.get_session(
            app_name=APP_NAME_FOR_ADK, 
            user_id=USER_ID, 
            session_id=session_id
        ))
        
        if not existing_session:
            asyncio.run(session_service.create_session(
                app_name=APP_NAME_FOR_ADK,
                user_id=USER_ID,
                session_id=session_id,
                state=INITIAL_STATE
            ))
            
    return runner, session_id

async def run_adk_async(runner: Runner, session_id: str, user_message_text: str):
    # FIX: Await the session retrieval here
    session = await runner.session_service.get_session(
        app_name=APP_NAME_FOR_ADK, 
        user_id=USER_ID, 
        session_id=session_id
    )
    
    if not session:
        return "Error: ADK session not found."

    content = genai_types.Content(role='user', parts=[genai_types.Part(text=user_message_text)])
    final_response_text = "[Agent encountered an issue]" 

    async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=content):
        if event.is_final_response(): 
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            break 
    return final_response_text
