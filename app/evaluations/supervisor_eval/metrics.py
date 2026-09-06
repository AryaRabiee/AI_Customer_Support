import json
from pathlib import Path

current_dir = Path(__file__).parent


def accuracy():

    with open(current_dir / "result_supervisor.json", "r", encoding="utf-8") as data:
        dataset = json.load(data)

    correct = sum(
        item["expected"] == item["response"].strip()
        for item in dataset
    )

    accuracy = correct / len(dataset)

    print(f"Correct: {correct}")
    print(f"Total: {len(dataset)}")
    print(f"Accuracy: {accuracy:.2%}")

accuracy()