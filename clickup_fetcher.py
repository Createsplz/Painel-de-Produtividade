import requests
import json
from datetime import datetime

# Lê token e team_id
with open("config.json") as f:
    config = json.load(f)

CLICKUP_API_TOKEN = config["clickup_token"]

# IDs das listas que você quer monitorar
LIST_IDS = [
    "901306837552",  # Produção de Conteúdo
    "901306838039",  # Produção de Vídeos
    "901306838056",  # Produção de Design
]

# Status que define "concluído"
TARGET_STATUS = "concluído"

headers = {
    "Authorization": CLICKUP_API_TOKEN
}

all_tasks = []

for list_id in LIST_IDS:
    url = f"https://api.clickup.com/api/v2/list/{list_id}/task?status={TARGET_STATUS}&include_closed=true"
    response = requests.get(url, headers=headers)
    data = response.json()

    for task in data.get("tasks", []):
        task_data = {
            "id": task["id"],
            "name": task["name"],
            "assignees": [a["username"] for a in task.get("assignees", [])],
            "tags": [t["name"] for t in task.get("tags", [])],
            "date_closed": datetime.fromtimestamp(int(task["date_closed"]) / 1000).strftime("%Y-%m-%d") if task.get("date_closed") else None
        }
        all_tasks.append(task_data)

# Salva as tarefas em um arquivo local
with open("clickup_tasks.json", "w") as f:
    json.dump(all_tasks, f, indent=2)

print(f"✅ {len(all_tasks)} tarefas concluídas salvas em clickup_tasks.json")
