# frontend/app.py
import streamlit as st
import requests
from PyPDF2 import PdfReader

# Backend API URL
API_URL = "http://127.0.0.1:5000/chat"

# Streamlit page setup
st.set_page_config(page_title="🌱 Ayurveda & Panchakarma Chatbot", page_icon="🌿", layout="centered")

# Custom CSS for chat container
st.markdown(
    """
    <style>
        /* Page background */
        .reportview-container, .main, .block-container {
            background-color: white;  /* Set page background to white */
        }

        /* Chat container */
        .chat-messages {
            flex-grow: 1;
            overflow-y: auto;
            padding-right: 10px;
            margin-bottom: 15px;
            background-color: #f9f9f9;  /* Slight gray for chat area */
            border-radius: 12px;
        }

        /* Chat messages */
        .chat-message {
            padding: 20px 40px;
            border-radius: 12px;
            margin: 10px 0;
            max-width: 90%;
            word-wrap: break-word;
            font-size: 15px;
            color: black;
        }
        .chat-message.user {
            background-color: #DCF8C6;
            margin-left: auto;
            text-align: right;
        }
        .chat-message.assistant {
            background-color: #f1f1f1;
            margin-right: auto;
            text-align: left;
        }

        /* Input row */
        .chat-input-row {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Input box */
        .stTextInput textarea {
            border-radius: 8px;
            flex-grow: 1;
        }

        /* File uploader inline and longer */
        .stFileUploader {
            flex:1;
            max-width: 200px;
            margin: 5;
        }

        /* Optional: align input and file uploader in one line */
        .stForm .stFormContent {
            display: flex;
            gap: 10px;
            align-items: center;
        }
    </style>
    """,
    unsafe_allow_html=True
)



# Title
st.markdown("<h2 style='text-align:center; color: black';>🌱 Ayurveda & Panchakarma Chatbot</h2>", unsafe_allow_html=True)

# Session state to store messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Namaste! 🌿 Ask me anything about Ayurveda or Panchakarma therapies."}
    ]

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Messages area
st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "assistant"
    st.markdown(
        f'<div class="chat-message {role_class}"><b>{msg["role"].capitalize()}:</b> {msg["content"]}</div>',
        unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# Input row (message + buttons)
with st.container():
    col1, col2, col3, col4 = st.columns([15, 3, 3, 9])
    with col1:
        user_input = st.text_input("Type your message...", key="input", label_visibility="collapsed")
    with col2:
        send_pressed = st.button("📤", use_container_width=True)
    with col3:
        voice_pressed = st.button("🎤", use_container_width=True)
    with col4:
        uploaded_pdf = st.file_uploader("📄", type="pdf", label_visibility="collapsed")

# Handle send
if send_pressed and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Bot is thinking..."):
        response = requests.post(API_URL, json={"messages": st.session_state.messages}).json()

        if "error" in response:
            st.error(response["error"])
        else:
            reply = response["reply"]
            st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# Handle voice button (placeholder)
if voice_pressed:
    st.info("🎙️ Voice input feature coming soon!")

# Handle PDF upload
if uploaded_pdf:
    pdf_reader = PdfReader(uploaded_pdf)
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text() + "\n"
    st.session_state.messages.append({"role": "user", "content": f"Here is the uploaded document:\n{pdf_text}"})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
