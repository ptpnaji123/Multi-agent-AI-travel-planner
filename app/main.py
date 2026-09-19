from app.graph.graph import build_graph


def main():

    graph = build_graph()

    initial_state = {
        "user_request": (
            "I want to travel from Kochi to Dubai "
            "for 5 days with a budget of 150000 INR."
        )
    }

    result = graph.invoke(initial_state)

    print("\n--- GRAPH COMPLETED ---")

    print(result)


if __name__ == "__main__":
    main()