import sys
import requests

client_id = "IWUL07BVON14EQ2DWRM8PL2DLNGC1O8N"
client_secret = "XETW40VKT017MUH5Z8OI0Y6OOWF96BLCEQO92KA5YBLJH3J5MX16RYITVC65KNSW"
redirect_uri = "https://5a93-45-228-241-81.ngrok-free.app"

if len(sys.argv) != 2:
    print("Uso: python3 get_token.py WMPY9MFR70I42HEP3KFU3L1QICK7WPXE")
    sys.exit(1)

auth_code = sys.argv[1]

url = "https://api.clickup.com/api/v2/oauth/token"

data = {
    "client_id": client_id,
    "client_secret": client_secret,
    "code": auth_code,
    "redirect_uri": redirect_uri
}

response = requests.post(url, data=data)

if response.status_code == 200:
    token = response.json()["access_token"]
    print("\n✅ Seu access_token é:\n")
    print(token)
else:
    print("❌ Erro ao obter token:", response.text)
