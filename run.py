from app.graph.graph import build_graph


def main():

    graph = build_graph()

    initial_state = {
        "user_request": (
            "I want to travel from Kochi to Dubai "
            "for 5 days from December 10 to December 15, 2026."
        )
    }

    result = graph.invoke(initial_state)

    print("\n--- GRAPH COMPLETED ---")

    print("\nFinal State:")
    print(result)


if __name__ == "__main__":
    main()