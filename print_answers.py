import json
with open('artifacts/actual_answers.json') as f:
    data = json.load(f)
for a in data['answers']:
    if a['id'] in ['A01', 'A02', 'E03']:
        print(f"ID: {a['id']}")
        print(f"Q: {a['question']}")
        print(f"A: {a['actual_answer']}")
        print()