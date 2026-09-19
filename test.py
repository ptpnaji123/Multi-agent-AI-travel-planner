from app.rag.vectorstore import get_vectorstore


def main():

    vectorstore = get_vectorstore()

    results = vectorstore.similarity_search(
        "What are the main transportation options in Dubai?",
        k=3,
    )

    print("\n--- RAG RESULTS ---")

    for result in results:

        print("\nSource:")
        print(result.metadata.get("source"))

        print("\nContent:")
        print(result.page_content)


if __name__ == "__main__":
    main()