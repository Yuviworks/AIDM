import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CHROMA_PATH = BASE_DIR / "rag" / "chroma_db"

ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


# ============================================================
# MODEL → VECTOR DATABASE MAPPING
# ============================================================

MODEL_DATABASES = {
    "KENT Elegant": CHROMA_PATH / "kent_elegant",
    "KENT Grand": CHROMA_PATH / "kent_grand",
    "KENT Sterling Star": CHROMA_PATH / "kent_sterling_star",
}


# ============================================================
# EMBEDDINGS
# ============================================================

def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# ============================================================
# GET MODEL-SPECIFIC VECTOR DATABASE
# ============================================================

def get_vector_database(model: str):

    if model not in MODEL_DATABASES:

        raise ValueError(
            f"Unsupported appliance model: {model}"
        )

    persist_directory = MODEL_DATABASES[model]

    if not persist_directory.exists():

        raise FileNotFoundError(
            f"Vector database not found for {model}. "
            f"Expected location: {persist_directory}"
        )

    embeddings = get_embeddings()

    collection_name = (
        model
        .lower()
        .replace(" ", "_")
    )

    vectorstore = Chroma(
        persist_directory=str(persist_directory),
        embedding_function=embeddings,
        collection_name=collection_name
    )

    return vectorstore


# ============================================================
# SEARCH MODEL-SPECIFIC KNOWLEDGE
# ============================================================

def search_knowledge(
    query: str,
    model: str
):

    vectorstore = get_vector_database(model)

    results = vectorstore.similarity_search(
        query,
        k=3
    )

    return results


# ============================================================
# GENERATE RAG ANSWER
# ============================================================

def generate_rag_answer(
    query: str,
    model: str
):

    # --------------------------------------------------------
    # Validate model
    # --------------------------------------------------------

    if model not in MODEL_DATABASES:

        raise ValueError(
            f"Unsupported appliance model: {model}"
        )


    # --------------------------------------------------------
    # Retrieve knowledge ONLY from selected model
    # --------------------------------------------------------

    documents = search_knowledge(
        query=query,
        model=model
    )


    if not documents:

        return {
            "query": query,
            "model": model,
            "answer": (
                f"The available {model} maintenance manual "
                "does not contain enough information to answer "
                "this question."
            ),
            "retrieved_context": [],
            "sources": []
        }


    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context = "\n\n".join(
        document.page_content
        for document in documents
    )


    # --------------------------------------------------------
    # Get source manuals
    # --------------------------------------------------------

    sources = list(
        dict.fromkeys(
            document.metadata.get(
                "source_manual",
                f"{model} manual"
            )
            for document in documents
        )
    )


    # --------------------------------------------------------
    # Get Groq API key
    # --------------------------------------------------------

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:

        raise ValueError(
            "GROQ_API_KEY was not found in the .env file."
        )


    # --------------------------------------------------------
    # Initialize LLM
    # --------------------------------------------------------

    llm = ChatGroq(
        api_key=api_key,
        model="openai/gpt-oss-120b",
        temperature=0.2
    )


    # --------------------------------------------------------
    # RAG Prompt
    # --------------------------------------------------------

    prompt = f"""
You are AIDM, an intelligent appliance maintenance assistant.

The user is asking about this specific appliance model:

{model}

IMPORTANT RULES:

1. Answer ONLY using the retrieved information provided below.

2. Use ONLY information belonging to the selected
   appliance model: {model}.

3. Do NOT mix information from other appliance models.

4. Do NOT invent maintenance intervals, technical
   specifications, replacement schedules, procedures,
   service requirements, or safety instructions.

5. If the retrieved information does not contain enough
   information to answer the question, clearly say that
   the available {model} manual does not contain enough
   information.

6. Keep the answer concise and easy to understand.

Selected Appliance Model:
-------------------------
{model}
-------------------------

Retrieved Maintenance Knowledge:
--------------------------------
{context}
--------------------------------

User Question:
--------------
{query}
--------------

Provide the maintenance answer.
"""


    # --------------------------------------------------------
    # Generate response
    # --------------------------------------------------------

    response = llm.invoke(prompt)


    # --------------------------------------------------------
    # Return structured response
    # --------------------------------------------------------

    return {
        "query": query,
        "model": model,
        "answer": response.content,
        "retrieved_context": [
            document.page_content
            for document in documents
        ],
        "sources": sources
    }