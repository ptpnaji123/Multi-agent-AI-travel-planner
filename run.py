from app.graph.graph import build_graph


def main():

    user_request = (
        "I want to travel from Kochi to Dubai "
        "for 5 days from December 10 to "
        "December 15, 2026."
    )

    graph = build_graph()

    initial_state = {
        "user_request": user_request
    }

    final_state = graph.invoke(
        initial_state
    )

    print("\n--- GRAPH COMPLETED ---")

    print("\nFinal State:")

    print(final_state)


if __name__ == "__main__":
    main()