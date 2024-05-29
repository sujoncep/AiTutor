import streamlit as st
import os
from groq import Groq
import random

from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate


def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """
    
    # Get Groq API key
    groq_api_key = os.environ['GROQ_API_KEY']

    # The title and greeting message of the Streamlit application
    st.title("Chat with AI Tutor")
    st.write("Hello! I'm your friendly AI Tutor. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!")

    # Set default system prompt and model
    system_prompt = "You are a helpful AI assistant."
    model = 'llama3-8b-8192'
    conversational_memory_length = 10  # Set maximum memory length to 10

    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

    # session state variable
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    else:
        for message in st.session_state.chat_history:
            memory.save_context(
                {'input': message['human']},
                {'output': message['AI']}
            )

    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(
        groq_api_key=groq_api_key, 
        model_name=model
    )

    # Input for user question
    user_question = st.text_input("Ask a question:", key="input")

    # If the user has asked a question,
    if user_question:
        # Construct a chat prompt template using various components
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=system_prompt
                ),  # This is the persistent system prompt that is always included at the start of the chat.

                MessagesPlaceholder(
                    variable_name="chat_history"
                ),  # This placeholder will be replaced by the actual chat history during the conversation. It helps in maintaining context.

                HumanMessagePromptTemplate.from_template(
                    "{human_input}"
                ),  # This template is where the user's current input will be injected into the prompt.
            ]
        )

        # Create a conversation chain using the LangChain LLM (Language Learning Model)
        conversation = LLMChain(
            llm=groq_chat,  # The Groq LangChain chat object initialized earlier.
            prompt=prompt,  # The constructed prompt template.
            verbose=True,   # Enables verbose output, which can be useful for debugging.
            memory=memory,  # The conversational memory object that stores and manages the conversation history.
        )
        
        # The chatbot's answer is generated by sending the full prompt to the Groq API.
        response = conversation.predict(human_input=user_question)
        message = {'human': user_question, 'AI': response}
        st.session_state.chat_history.append(message)

    # Display the chat history with styling
    user_icon = "😊"
    ai_icon = "🤖"

    # Colors that work well in both dark and light modes
    user_message_style = "background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px; color: black;"
    ai_message_style = "background-color: #e8f4fc; padding: 10px; border-radius: 10px; margin-bottom: 10px; color: black;"

    for message in st.session_state.chat_history:
        st.markdown(f"<div style='{user_message_style}'><b>{user_icon} You:</b> {message['human']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='{ai_message_style}'><b>{ai_icon} Chatbot:</b> {message['AI']}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()