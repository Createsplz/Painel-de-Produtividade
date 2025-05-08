import requests
import json

# Lê token e ID da equipe do arquivo config.json
with open("config.json") as f:
    config = json.load(f)

CLICKUP_API_TOKEN = config["clickup_token"]
TEAM_ID = config["team_id"]

def get_team_members():
    url = f"https://api.clickup.com/api/v2/team/{TEAM_ID}"
    headers = {"Authorization": CLICKUP_API_TOKEN}
    response = requests.get(url, headers=headers)
    data = response.json()

    print("\n🔎 RESPOSTA BRUTA DA API:")
    print(json.dumps(data, indent=2))

    if "team" not in data or "members" not in data["team"]:
        print("❌ Resposta da API inválida. Verifique o token e o team_id.")
        return []

    members = data["team"]["members"]

    print(f"\n✅ Membros encontrados: {len(members)}")

    return [
        {
            "id": m["user"]["id"],
            "name": m["user"]["username"],
            "avatar": m["user"].get("profilePicture") or "https://via.placeholder.com/50"
        }
        for m in members
    ]


# ✅ 3. Buscar tarefas por usuário
def get_user_tasks(user_id):
    url = f"https://api.clickup.com/api/v2/user/{user_id}/task?include_closed=true"
    headers = {"Authorization": CLICKUP_API_TOKEN}
    response = requests.get(url, headers=headers)
    tasks = response.json().get("tasks", [])
    return tasks

# ✅ 4. Resumo de tarefas
def summarize_tasks(tasks):
    total = len(tasks)
    completed = len([
        t for t in tasks
        if t.get("status", {}).get("status", "").lower() in ["concluído", "done"]
    ])
    open_tasks = total - completed
    return total, open_tasks, completed
