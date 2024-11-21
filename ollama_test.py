from ollama import LLMIntegration


def main():
    # Initialize the LLM Integration with appropriate settings
    llm = LLMIntegration(base_url="http://localhost:11434",
                         model="llama3.1:latest")

    # Test case 1: Reformulate Query
    user_query = "recent advancements in nuclear fusion"
    print("\n--- Test 1: Reformulate Query ---")
    reformulated_query = llm.reformulate_query(user_query)
    if reformulated_query:
        print(f"Original Query: {user_query}")
        print(f"Reformulated Query: {reformulated_query}")
    else:
        print("Reformulation failed.")

    # Test case 2: Analyze Content
    test_content = (
        "Nuclear fusion is a process that powers the stars. Recently, scientists have made "
        "significant progress in achieving sustained nuclear fusion in laboratory conditions."
    )
    print("\n--- Test 2: Analyze Content ---")
    analyzed_content = llm.analyze_content(test_content)
    if analyzed_content:
        print(f"Original Content: {test_content}")
        print(f"Analysis/Summary: {analyzed_content}")
    else:
        print("Content analysis failed.")

    # Test case 3: Generate Final Answer
    query = "What are the recent advancements in nuclear fusion?"
    content = (
        "Scientists at JET achieved a breakthrough by generating 59 megajoules of energy. "
        "This marks a significant step toward practical nuclear fusion as a clean energy source."
    )
    print("\n--- Test 3: Generate Final Answer ---")
    final_answer = llm.generate_final_answer(query, content)
    if final_answer:
        print(f"Query: {query}")
        print(f"Content: {content}")
        print(f"Generated Answer: {final_answer}")
    else:
        print("Final answer generation failed.")


if __name__ == "__main__":
    main()
