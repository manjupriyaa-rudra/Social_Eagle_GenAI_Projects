import streamlit as st
import tempfile
import asyncio

from PIL import Image
from utilities.vision_service import image_to_text
from pipeline.knowledge_graph import KnowledgeGraphRAG
from pipeline.hybrid_retriever import HybridRetriever
from utilities.chat_service import ask_question


st.set_page_config(page_title="Hybrid KG-RAG Assistant", layout="wide")
st.title("Hybrid KG-RAG Architecture Assistant")


# -------------------------
# Initialize KG and Hybrid
# -------------------------
if "kg" not in st.session_state:
    st.session_state.kg = KnowledgeGraphRAG()

if "hybrid" not in st.session_state:
    st.session_state.hybrid = None

kg = st.session_state.kg
hybrid = st.session_state.get("hybrid", None)


# -------------------------
# Safe async runner
# -------------------------
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        return asyncio.ensure_future(coro)
    else:
        return loop.run_until_complete(coro)


# -------------------------
# Session state
# -------------------------
if "architecture_text" not in st.session_state:
    st.session_state.architecture_text = None


# -------------------------
# Upload section
# -------------------------
st.subheader("Upload Diagram")

uploaded = st.file_uploader(
    "Upload architecture diagram",
    type=["png", "jpg", "jpeg"]
)

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded Diagram")

    if st.button("Process Diagram"):

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            image.save(tmp.name)
            image_path = tmp.name

        # 1. Extract text from image
        with st.spinner("Extracting architecture..."):
            text = image_to_text(image_path)

        # Store extracted text
        st.session_state.architecture_text = text

        # 2. Ingest into Knowledge Graph (SYNC — no run_async)
        with st.spinner("Building knowledge graph..."):
            st.session_state.kg.ingest(text)

            # 3. Initialize hybrid retriever
            st.session_state.hybrid = HybridRetriever([text])

        # 4. Show extracted text
        st.subheader("Extracted Architecture")
        st.write(text)

        st.success("Diagram processed successfully!")

# -------------------------
# Show loaded architecture
# -------------------------
if st.session_state.architecture_text:
    st.subheader("Loaded Architecture")
    st.write(st.session_state.architecture_text)


# ------------------------------
# Chat
# ------------------------------
question = st.chat_input("Ask a question about the diagram")

if question:
    hybrid = st.session_state.get("hybrid", None)

    if hybrid is None:
        st.warning("Please process a diagram first.")
        st.stop()

    with st.chat_message("user"):
        st.write(question)

    answer = ask_question(
        question,
        st.session_state.kg,
        hybrid
    )

    with st.chat_message("assistant"):
        st.write(answer)



# -------------------------
# Reset button
# -------------------------
if st.session_state.architecture_text:
    if st.button("Reset Diagram"):
        st.session_state.architecture_text = None
        st.rerun()
