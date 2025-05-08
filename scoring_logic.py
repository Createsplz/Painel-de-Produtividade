import json

# Lê a lógica de pontuação externa
with open("pontuacoes.json") as f:
    SCORING_RULES = json.load(f)

DEFAULT_SCORE = 2

# Lê as tarefas do ClickUp
with open("clickup_tasks.json") as f:
    tasks = json.load(f)

processed = []

for task in tasks:
    title = task["name"].lower()
    tags = [t.lower() for t in task.get("tags", [])]
    assignees = task.get("assignees", [])
    date = task.get("date_closed")

    score = DEFAULT_SCORE

    for keyword, points in SCORING_RULES.items():
        if keyword in title or keyword in tags:
            score = points
            break

    for person in assignees:
        processed.append({
            "responsavel": person,
            "titulo": task["name"],
            "tags": task.get("tags", []),
            "data": date,
            "pontos": score
        })

# Salva as tarefas pontuadas
with open("processed_tasks.json", "w") as f:
    json.dump(processed, f, indent=2, ensure_ascii=False)

print(f"✅ {len(processed)} tarefas pontuadas com base no arquivo pontuacoes.json")
