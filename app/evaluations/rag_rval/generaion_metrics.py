
from langchain_openai import ChatOpenAI
from datasets import Dataset
from langchain_openai import ChatOpenAI
import json
from pathlib import Path
from app.utils.prompts import CORRECTNESS_PROMPT  ,FAITHFULNESS_PROMPT ,RELEVANCE_PROMPT
import os
current_dir = Path(__file__).parent

api_key = os.getenv("GPT_API_KEY")
base_url = os.getenv("BASE_URL_GAP")
model = ChatOpenAI(
    model="gpt-5.6-luna",
    api_key=api_key,
    base_url=base_url,
    timeout=30,
    max_retries=2
)

def rag_evaluation_correctness():

    with open(current_dir/"final_dataset_generation.json","r",encoding="utf-8")as f:
        dataset = json.load(f)

    results = []
    for item in dataset:
        question = item["question"]
        ground_truth = item["ground_truth"]
        rag_answer = item["rag_answer"]

        prompt = CORRECTNESS_PROMPT.format(
            question=question,
            ground_truth=ground_truth,
            rag_answer=rag_answer
        )
        response = model.invoke(prompt)
        results.append({
            "id": item["id"],
            "question": question,
            "ground_truth": ground_truth,
            "rag_answer": rag_answer,
            "evaluation": response.content
        })

    with open(current_dir / "correctness_results.json","w",encoding="utf-8") as f:
        
        json.dump(results,f ,ensure_ascii=False,indent=4)
    return results


def rag_evaluation_relevance():
    with open(current_dir/"final_dataset_generation.json","r",encoding="utf-8")as f:
        dataset = json.load(f)

    results = []
    for item in dataset:
        question = item["question"]
        ground_truth = item["ground_truth"]
        rag_answer = item["rag_answer"]

        prompt = RELEVANCE_PROMPT.format(
            question=question,
            ground_truth=ground_truth,
            rag_answer=rag_answer
        )
        response = model.invoke(prompt)
        results.append({
            "id": item["id"],
            "question": question,
            "ground_truth": ground_truth,
            "rag_answer": rag_answer,
            "evaluation": response.content
        })

    with open(current_dir / "relevance_results.json","w",encoding="utf-8") as f:
        
        json.dump(results,f ,ensure_ascii=False,indent=4)
    return results

with open(current_dir/"correctness_results.json","r",encoding="utf-8")as f:
    dataset = json.load(f)
    correctness_scores = []

    for item in dataset:
        evaluation = json.loads(item["evaluation"])
        correctness_scores.append(evaluation["score"])

with open(current_dir/"relevance_results.json","r",encoding="utf-8")as f:
    dataset = json.load(f)
    relevance_scores = []

    for item in dataset:
        evaluation = json.loads(item["evaluation"])
        relevance_scores.append(evaluation["score"])


average_correctness = sum(correctness_scores) / len(correctness_scores)
average_relevance= sum(relevance_scores) / len(relevance_scores)
print("average_correctness is" , average_correctness)
print("average_relevance is" , average_relevance)


