
from datapilot.services.llm_service import ask_llm

if __name__ == "__main__":
    # Make one real API request to verify the integration.
    answer = ask_llm(
        "In one sentence, explain what DataPilot does."
    )
    print(answer)
