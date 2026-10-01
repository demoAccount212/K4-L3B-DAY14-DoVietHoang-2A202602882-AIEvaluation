#!/usr/bin/env python
"""Generate actual answers using Gemini generator."""

from domain_assistant import (
    DomainAssistant, load_corpus, BM25Retriever, GeminiGenerator
)
import json
from pathlib import Path

def main():
    print("Loading corpus...")
    corpus_id, chunks = load_corpus("data/technology_store")
    print(f"Loaded {len(chunks)} chunks from corpus: {corpus_id}")

    print("Initializing DomainAssistant with GeminiGenerator...")
    assistant = DomainAssistant(corpus_id, BM25Retriever(chunks), GeminiGenerator())

    print("Loading golden dataset...")
    with open("golden_dataset.json", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Generating answers for {len(dataset['qa_pairs'])} questions...")
    answers = []
    for i, qa in enumerate(dataset["qa_pairs"], 1):
        print(f"  [{i}/{len(dataset['qa_pairs'])}] {qa['id']}: {qa['question'][:60]}...")
        try:
            answer = assistant.answer(qa["question"])
            answers.append({
                "id": qa["id"],
                "question": qa["question"],
                "actual_answer": answer,
                "retrieved_contexts": [
                    {"source_doc": chunk.source_doc, "chunk_id": chunk.chunk_id, "text": chunk.text, "score": round(chunk.score, 6)}
                    for chunk in assistant.retriever.retrieve(qa["question"], assistant.top_k)
                ],
                "error": None
            })
            print(f"    OK ({len(answer)} chars)")
        except Exception as e:
            print(f"    FAILED: {e}")
            answers.append({
                "id": qa["id"],
                "question": qa["question"],
                "actual_answer": "",
                "retrieved_contexts": [],
                "error": str(e)
            })

    artifact = {
        "schema_version": "1.0",
        "corpus_id": corpus_id,
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
        "agent": {
            "name": "domain-assistant",
            "model": assistant.generator.model,
            "top_k": assistant.top_k,
            "prompt_version": "1.0",
        },
        "answers": answers,
    }

    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "actual_answers.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(answers)} actual answers to {output_path}")

if __name__ == "__main__":
    main()