#!/usr/bin/env python3
import json
import requests

# Carregar configuração
with open('Config/DefectDojo.json', 'r') as f:
    config = json.load(f)

url = f"{config['defectdojo']['url']}/api/v2/findings/"
headers = {'Authorization': f"Token {config['defectdojo']['api_key']}"}
params = {'severity': 'Critical', 'limit': 1}

print("🔍 Testando API de findings...")
resposta = requests.get(url, headers=headers, params=params, verify=False)

if resposta.status_code == 200:
    dados = resposta.json()
    print(f"✅ Status: {resposta.status_code}")
    print(f"📊 Findings encontrados: {dados.get('count', 0)}")
    if dados.get('results'):
        print(f"📋 Primeiro finding: {dados['results'][0]['title']}")
else:
    print(f"❌ Erro: {resposta.status_code}")
    print(resposta.text)