#!/usr/bin/env python3
"""
PROJETO: AUTOMAÇÃO COM DEFECTDOJO
Demonstração para Mentor - Versão Funcional
Autor: Thiago Santos Vilas Boas
"""
import json
import requests
import os
os.system("")
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def main():
    print("="*60)
    print(f"{BOLD}{RED}SCRIPT BLUETEAM - DEFECTDOJO INTEGRATION{RESET}")
    print("="*60)
    
    # 1. Carregar configuração
    print("\nCARREGANDO CONFIGURAÇÃO...")
    
    # Caminho CORRETO: a partir da pasta onde este script está
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'Config', 'DefectDojo.json')
    
    print(f"Caminho do config: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print("Configuração carregada com sucesso")
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
        print("\nVERIFIQUE:")
        print(f"1. O arquivo existe? ls {config_path}")
        print(f"2. Permissões corretas?")
        return
    
    dd = config['defectdojo']
    print(f"\nCONFIGURAÇÃO CARREGADA:")
    print(f"   • URL: {dd['url']}")
    print(f"   • Engagement ID: {dd['engagement_id']}")
    print(f"   • API Key: {dd['api_key'][:8]}...{dd['api_key'][-8:]}")
    
    # 2. Testar conexão
    print("\nTESTANDO CONEXÃO COM API...")
    headers = {'Authorization': f'Token {dd["api_key"]}'}
    
    try:
        r = requests.get(dd['url'], headers=headers, verify=False, timeout=5)
        if r.status_code == 200:
            print("API conectada com sucesso!")
            print(f"   Status: {r.status_code}")
        else:
            print(f" Erro HTTP: {r.status_code}")
            print(f"   Resposta: {r.text[:100]}")
            return
    except Exception as e:
        print(f" Falha na conexão: {e}")
        print("\nVERIFIQUE:")
        print("  1. O Docker do DefectDojo está rodando?")
        print("  2. docker-compose ps (no diretório django-DefectDojo)")
        return
    
    # 3. Buscar vulnerabilidades
    print("\n3  ANALISANDO VULNERABILIDADES...")
    findings_url = f"{dd['url']}findings/"
    params = {'engagement': dd['engagement_id'], 'limit': 50}
    
    try:
        r = requests.get(findings_url, headers=headers, params=params, verify=False)
        if r.status_code == 200:
            data = r.json()
            total = data.get('count', 0)
            
            print(f"\n RESULTADOS ENCONTRADOS:")
            print(f"   • Total de vulnerabilidades: {total}")
            
            # Contar por severidade
            severities = ['Critical', 'High', 'Medium', 'Low', 'Info']
            print(f"\n DISTRIBUIÇÃO POR GRAVIDADE:")
            for severity in severities:
                params['severity'] = severity
                r_sev = requests.get(findings_url, headers=headers, params=params, verify=False)
                if r_sev.status_code == 200:
                    count = r_sev.json().get('count', 0)
                    if count > 0:
                        bar = "█" * min(count, 20)  # Barra gráfica
                        print(f"   • {severity:8s}: {count:3d} {bar}")
            
            # Mostrar exemplos
            if total > 0:
                print(f"\nEXEMPLOS DE VULNERABILIDADES (3 primeiras):")
                print("   " + "-"*50)
                for i, vuln in enumerate(data.get('results', [])[:3], 1):
                    print(f"\n   {i}. {vuln.get('title', 'Sem título')[:70]}...")
                    print(f"      ID: {vuln.get('id', 'N/A')} | Severity: {vuln.get('severity', 'N/A')}")
        # Usa .get() para evitar erro se a chave não existir
                    print(f"      Status: {vuln.get('status', 'None')} | Active: {'Sim' if vuln.get('active') else 'Não'}")
                if vuln.get('cve'):
                    print(f"      CVE: {vuln['cve']}")
                    
        else:
            print(f"Erro ao buscar dados: {r.status_code}")
            print(f"   Resposta: {r.text[:100]}")
            
    except Exception as e:
        print(f"Erro na análise: {e}")
    
    print("\n" + "="*60)
    print(" DEMONSTRAÇÃO CONCLUÍDA")
    print("\n O QUE FOI IMPLEMENTADO:")
    print("   1.  Leitura de configuração JSON")
    print("   2.  Autenticação via API Token")
    print("   3.  Consulta à API REST do DefectDojo")
    print("   4.  Análise e apresentação de dados")
    print("\n PRÓXIMOS PASSOS:")
    print("   1.  Bulk update de vulnerabilidades")
    print("   2. Importação automática de scans")
    print("   3.  Geração de relatórios PDF/HTML")
    print("="*60)

if __name__ == "__main__":
    main()
