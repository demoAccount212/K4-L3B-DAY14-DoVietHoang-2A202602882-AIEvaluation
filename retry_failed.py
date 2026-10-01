#!/usr/bin/env python
"""Retry failed questions with rate limit handling."""

import time
import json
from domain_assistant import DomainAssistant, load_corpus, BM25Retriever, GeminiGenerator
from pathlib import Path

def main():
    # Load existing answers
    with open("artifacts/actual_answers.json", encoding="utf-8") as f:
        artifact = json.load(f)

    # Load corpus and assistant
    corpus_id, chunks = load_corpus("data/technology_store")
    assistant = DomainAssistant(corpus_id, BM25Retriever(chunks), GeminiGenerator())

    # Load golden dataset for questions
    with open("golden_dataset.json", encoding="utf-8") as f:
        dataset = json.load(f)
    qa_map = {qa["id"]: qa["question"] for qa in dataset["qa_pairs"]}

    # Retry failed answers
    for i, ans in enumerate(artifact["answers"]):
        if ans.get("error"):
            qid = ans["id"]
            print(f"Retrying {qid}...")
            time.sleep(35)  # Wait for rate limit to reset
            try:
                question = qa_map[qid]
                answer = assistant.answer(question)
                retrieved = assistant.retriever.retrieve(question, assistant.top_k)
                artifact["answers"][i] = {
                    "id": qid,
                    "question": question,
                    "actual_answer": answer,
                    "retrieved_contexts": [
                        {"source_doc": c.source_doc, "chunk_id": c.chunk_id, "text": c.text, "score": round(c.score, 6)}
                        for c in retrieved
                    ],
                    "error": None
                }
                print(f"  OK ({len(answer)} chars)")
            except Exception as e:
                print(f"  Still failed: {e}")

    # Save updated artifact
    with open("artifacts/actual_answers.json", "w", encoding="utf-8") as f:
        json.dump(artifact, f, ensure_ascii=False, indent=2)
    print("Updated artifacts/actual_answers.json")

if __name__ == "__main__":
    main()