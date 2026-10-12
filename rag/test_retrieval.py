import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.rag_service import search_knowledge


if __name__ == "__main__":

    query = "Why does my water purifier need regular maintenance?"

    print("\nSearching AIDM knowledge base...")
    print("Query:", query)
    print("\nRetrieved information:\n")

    results = search_knowledge(query)

    for i, document in enumerate(results, start=1):

        print(f"--- Result {i} ---")
        print(document.page_content)
        print()