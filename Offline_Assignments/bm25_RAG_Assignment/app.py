# ================================
# BM25 RAG Chatbot for CBSE 6th Std
# Streamlit + LangChain
# ================================

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi
from langchain_openai import ChatOpenAI

# NEW: Import system prompt from external file
from prompts import SYSTEM_PROMPT  # <-- ADDED

# ================================
# LOAD ENV
# ================================
print("Step 1: Loading environment variables...")
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ================================
# STREAMLIT UI
# ================================
st.set_page_config(page_title="CBSE Tutor Chatbot", layout="wide")

st.title("📚 CBSE 6th Std Tutor Chatbot")
st.caption("BM25-powered PDF Question Answering")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================================
# FILE UPLOAD
# ================================
uploaded_file = st.file_uploader("Upload CBSE PDF", type="pdf")

if uploaded_file:

    # Save PDF temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # ================================
    # LOAD PDF
    # ================================
    with st.spinner("Reading PDF..."):
        print("Step 2: Loading PDF...")
        loader = PyPDFLoader("temp.pdf")
        documents = loader.load()

    # ================================
    # SPLIT INTO CHUNKS
    # ================================
    with st.spinner("Splitting into chunks..."):
        print("Step 3: Splitting text into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,   # <-- Can be tuned
            chunk_overlap=100 # <-- Can be tuned
        )
        chunks = text_splitter.split_documents(documents)

    st.success(f"Loaded {len(chunks)} chunks")

    # ================================
    # BM25 INDEX
    # ================================
    print("Step 4: Building BM25 index...")

    corpus = [chunk.page_content.split() for chunk in chunks]
    bm25 = BM25Okapi(corpus)

    # ================================
    # CHAT DISPLAY
    # ================================
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ================================
    # USER INPUT
    # ================================
    query = st.chat_input("Ask a question...")

    if query:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                print("Step 5: Running BM25 retrieval...")
                print("\n--- BM25 DEBUG START ---")
                print("User query:", query)
                tokenized_query = query.split()
                scores = bm25.get_scores(tokenized_query)

                # Get top 4 chunks
                top_k = sorted(
                    list(enumerate(scores)),
                    key=lambda x: x[1],
                    reverse=True
                )[:4]

                retrieved_chunks = []
                for rank, (idx, score) in enumerate(top_k):
                #for idx, score in top_k:
                    chunk = chunks[idx]
                    page = chunk.metadata.get("page", "N/A")
                    print(f"\nRank {rank+1}")
                    print(f"Score: {score}")
                    print(f"Page: {page}")
                    print("Text preview:", chunk.page_content[:150])
                    retrieved_chunks.append(
                        f"(Page {page}) {chunk.page_content}"
                    )
                print("--- BM25 DEBUG END ---\n")    

                context = "\n\n".join(retrieved_chunks)

                print("Step 6: Sending to LLM...")

                llm = ChatOpenAI(
                    model="gpt-4o-mini",  # Cost-effective model
                    temperature=0
                )

                # UPDATED: Using external SYSTEM_PROMPT
                prompt = f"""
System:
{SYSTEM_PROMPT}

Context:
{context}

User Question:
{query}
"""

                response = llm.invoke(prompt)
                answer = response.content

                print("Step 7: Response generated.")

                st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
