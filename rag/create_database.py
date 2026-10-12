from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


BASE_DIR = Path(__file__).resolve().parents[1]

MANUALS_DIR = BASE_DIR / "manuals"
CHROMA_DIR = BASE_DIR / "rag" / "chroma_db"


MANUALS = {
    "KENT Elegant": MANUALS_DIR / "KENT_Elegant.txt",
    "KENT Grand": MANUALS_DIR / "KENT_Grand.txt",
    "KENT Sterling Star": MANUALS_DIR / "KENT_Sterling_Star.txt",
}


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def create_database(model_name, manual_path):
    print(f"\nCreating vector database for: {model_name}")
    print(f"Reading manual: {manual_path}")

    if not manual_path.exists():
        print(f"ERROR: Manual not found: {manual_path}")
        return

    loader = TextLoader(
        str(manual_path),
        encoding="utf-8"
    )

    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = text_splitter.split_documents(documents)

    # Add model information to every chunk
    for chunk in chunks:
        chunk.metadata["model"] = model_name
        chunk.metadata["source_manual"] = manual_path.name

    embeddings = get_embeddings()

    collection_name = (
        model_name
        .lower()
        .replace(" ", "_")
    )

    persist_directory = CHROMA_DIR / collection_name

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(persist_directory),
        collection_name=collection_name
    )

    print(f"Created database: {persist_directory}")
    print(f"Chunks created: {len(chunks)}")


def main():

    print("=" * 60)
    print("AIDM - KENT MODEL RAG DATABASE CREATION")
    print("=" * 60)

    for model_name, manual_path in MANUALS.items():
        create_database(
            model_name=model_name,
            manual_path=manual_path
        )

    print("\n" + "=" * 60)
    print("ALL KENT RAG DATABASES CREATED")
    print("=" * 60)


if __name__ == "__main__":
    main()