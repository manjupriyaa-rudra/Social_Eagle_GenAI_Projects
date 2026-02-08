# streamlit_app.py

import streamlit as st
import tempfile
import asyncio
from PIL import Image

from diagram_to_text import image_to_text
from ingest_diagram import ingest_architecture
from chat_service import ask_kg_question


# -----------------------------
# Create single event loop
# -----------------------------
if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)

loop = st.session_state.loop


# -----------------------------
# Session State Initialization
# -----------------------------
if "diagrams" not in st.session_state:
    st.session_state.diagrams = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_diagram" not in st.session_state:
    st.session_state.current_diagram = None


# -----------------------------
# Async-safe wrappers
# -----------------------------
def run_async(coro):
    return loop.run_until_complete(coro)


def process_diagram(image, diagram_name):
    async def run():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            image.save(tmp.name)
            image_path = tmp.name

        text = await image_to_text(image_path)
        kg_system = await ingest_architecture(text)
        st.session_state.diagrams[diagram_name] = kg_system
        st.session_state.current_diagram = diagram_name

    run_async(run())


def ask_question(question):
    async def run():
        diagram_name = st.session_state.current_diagram
        kg_system = st.session_state.diagrams.get(diagram_name)

        if not kg_system:
            return {
                "answer": "Please upload a diagram first.",
                "confidence": 0.0
            }

        from chat_service import ask_kg_question
        return await ask_kg_question(kg_system, question)

    return run_async(run())


# -----------------------------
# UI Layout
# -----------------------------
st.set_page_config(page_title="Architecture KG Chat", layout="wide")

st.title("🧠 Architecture Knowledge Graph Assistant")

# Sidebar
st.sidebar.header("Diagrams")

uploaded_file = st.sidebar.file_uploader(
    "Upload architecture diagram",
    type=["png", "jpg", "jpeg", "webp"]
)

diagram_name = st.sidebar.text_input(
    "Diagram name",
    placeholder="e.g., Mobile Backend"
)

if st.sidebar.button("Process Diagram"):
    if uploaded_file and diagram_name:
        image = Image.open(uploaded_file)
        with st.spinner("Processing diagram..."):
            process_diagram(image, diagram_name)
        st.sidebar.success(f"Diagram '{diagram_name}' processed.")
    else:
        st.sidebar.error("Upload a diagram and give it a name.")


# Diagram selector
if st.session_state.diagrams:
    selected = st.sidebar.selectbox(
        "Select active diagram",
        list(st.session_state.diagrams.keys())
    )
    st.session_state.current_diagram = selected


# Preview
if uploaded_file:
    st.sidebar.image(uploaded_file, caption="Diagram Preview", width=250)


# -----------------------------
# Chat Interface
# -----------------------------
st.subheader("Chat with your architecture")

# Display chat history
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(message)

# Chat input
user_input = st.chat_input("Ask a question about the architecture...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = ask_question(user_input)

            if isinstance(result, dict):
                answer_text = result.get("answer", "")
                confidence = result.get("confidence", 0.0)

                st.write(answer_text)
                st.caption(f"Confidence: {confidence*100:.0f}%")

                st.session_state.chat_history.append(("assistant", answer_text))
            else:
                st.write(result)
                st.session_state.chat_history.append(("assistant", result))



# Clear chat
if st.button("Clear Chat"):
    st.session_state.chat_history = []
