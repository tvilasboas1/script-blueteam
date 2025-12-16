#!/usr/bin/env python3
"""
TESTE DA API DEFECTDOJO - Versão Corrigida
"""
import json
import requests
import os

print("🎯 TESTE DA API DEFECTDOJO")
print("="*50)

# 1. Encontrar o arquivo de configuração CORRETAMENTE
script_dir = os.path.dirname(__file__)  # Pasta onde está este script
config_path = os.path.join(script_dir, '..', 'Config', 'DefectDojo.json')

print(f"🔍 Procurando configuração em: {config_path}")

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
    print("✅ Configuração carregada")
except Exception as e:
    print(f"❌ Erro ao carregar configuração: {e}")
    print("\n💡 SOLUÇÃO:")
    print("   O arquivo DefectDojo.json deve estar em: Config/DefectDojo.json")
    print("   Relativo a: /home/thiago-boas/Área de trabalho/CyberSegurança/Script BlueTeam")
    exit()

# 2. Preparar requisição
api_key = config['defectdojo']['api_key']
url = f"{config['defectdojo']['url']}findings/"
headers = {'Authorization': f'Token {api_key}'}
params = {'severity': 'Critical', 'limit': 1}

print(f"\n🔗 Testando: {url}")
print(f"📌 Parâmetros: {params}")
print(f"🔑 API Key: {api_key[:8]}...{api_key[-8:]}")

# 3. Fazer requisição
try:
    resposta = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
    
    print(f"\n📊 RESPOSTA DA API:")
    print(f"   Status: {resposta.status_code}")
    
    if resposta.status_code == 200:
        dados = resposta.json()
        print(f"   ✅ SUCESSO!")
        print(f"   Total de findings críticos: {dados.get('count', 0)}")
        
        if dados.get('results'):
            finding = dados['results'][0]
            print(f"\n📋 EXEMPLO DE VULNERABILIDADE:")
            print(f"   ID: {finding.get('id')}")
            print(f"   Título: {finding.get('title')}")
            print(f"   Severity: {finding.get('severity')}")
            print(f"   Status: {finding.get('status')}")
            print(f"   Active: {'Sim' if finding.get('active') else 'Não'}")
            
            if finding.get('cve'):
                print(f"   CVE: {finding.get('cve')}")
    else:
        print(f"   ❌ ERRO HTTP: {resposta.status_code}")
        print(f"   Mensagem: {resposta.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print(f"\n❌ CONEXÃO RECUSADA!")
    print("   O DefectDojo não está respondendo.")
    print("\n💡 SOLUÇÃO:")
    print("   1. Verifique se o Docker está rodando:")
    print("      cd ~/django-DefectDojo && docker-compose ps")
    print("   2. Se não estiver, inicie:")
    print("      docker-compose up -d")
    print("   3. Aguarde 30 segundos e tente novamente")
    
except Exception as e:
    print(f"\n❌ Erro inesperado: {type(e).__name__}: {e}")