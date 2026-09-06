import json
from pathlib import Path

current_dir = Path(__file__).parent
print(current_dir)
def recall_at_k(retrieved_chunks, ground_truth_chunks, k):

    retrieved = set(retrieved_chunks[:k])
    ground_truth = set(ground_truth_chunks)

    matched = retrieved & ground_truth

    return len(matched) / len(ground_truth)


def precision_at_k(retrieved_chunks, ground_truth_chunks, k):

    retrieved = set(retrieved_chunks[:k])
    ground_truth = set(ground_truth_chunks)

    matched = retrieved & ground_truth

    return len(matched) / len(retrieved) if retrieved else 0

def f1_at_k(precision , recall):
    return 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

relevant_chunks = []
retrieved_chunks = []
recalls = []
precisions = []
with open(f"{current_dir}/final_dataset_retrieval.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)
    for i in range(len(dataset)):
        relevant_chunks.append(dataset[i]["relevant_chunks"])
        retrieved_chunks.append(dataset[i]["retrieved_chunks"])

for retrieved, relevant in zip(retrieved_chunks, relevant_chunks):
    recall = recall_at_k(retrieved, relevant, 3)
    precision = precision_at_k(retrieved , relevant ,3)
    recalls.append(recall)
    precisions.append(precision)

average_recall = sum(recalls) / len(recalls)
average_precision = sum(precisions) / len(precisions)
f1 = f1_at_k(average_precision ,average_recall )
print("RECALL IS" , average_recall)
print("PRECISION IS " , average_precision)
print("F1 IS" , f1)
