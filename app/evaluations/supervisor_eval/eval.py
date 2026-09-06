
from langchain_openai import ChatOpenAI
from datasets import Dataset
import json
from pathlib import Path
from langchain.messages import SystemMessage , HumanMessage
from app.utils.prompts import SUPERVISOR_PROMPT
import os
current_dir = Path(__file__).parent

base_url = os.getenv("BASE_URL_GAP")
api_key = os.getenv("GPT_API_KEY")

model = ChatOpenAI(
    model="gpt-5.6-luna",
    api_key=api_key,
    base_url=base_url,
    
    timeout=30,
    max_retries=2
)

def format_conversation(conversation):
    if isinstance(conversation, str):
        return conversation

    return "\n".join(
        f'{message["role"]}: {message["content"]}'
        for message in conversation
    )

def supervisor_eval():
    with open(current_dir / "dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    results = []

    for item in dataset:
        conversation = format_conversation(item["conversation"])
        expected = item["answer"]

        response = model.invoke(
            [
                SystemMessage(content=SUPERVISOR_PROMPT),
                HumanMessage(content=conversation)
            ]
        )

        results.append({
            "expected": expected,
            "response": response.content,
        })

    with open("result_supervisor.json", "w", encoding="utf-8") as w:
        json.dump(results, w, ensure_ascii=False, indent=4)

    return results

supervisor_eval()