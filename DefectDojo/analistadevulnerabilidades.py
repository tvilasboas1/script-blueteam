#!/usr/bin/env python3
"""
Script de Análise de Vulnerabilidades - DefectDojo
Autor: Thiago Boas
Versão: 1.1 - Corrigido e melhorado
"""

import os
import json
import requests
from pathlib import Path

# ========== CONFIGURAÇÃO ==========
def carregar_configuracao():
    """Carrega configurações do arquivo JSON"""
    config_path = Path(__file__).parent.parent / "Config" / "DefectDojo.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✅ Configuração carregada: {config_path}")
        return config
    except FileNotFoundError:
        print(f"❌ Arquivo de configuração não encontrado: {config_path}")
        print("📁 Crie o arquivo Config/DefectDojo.json")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erro no JSON: {str(e)}")
        print("📝 Verifique a sintaxe do arquivo de configuração")
        return None

# ========== TESTE DE CONEXÃO ==========
def testar_conexao(config):
    """Testa conexão com API do DefectDojo - VERSÃO MELHORADA"""
    print("\n🔗 Testando conexão com DefectDojo...")
    
    # Tentar vários endpoints para maior robustez
    endpoints = [
        "/api/v2/users/current/",  # Usuário atual
        "/api/v2/users/",          # Lista de usuários
        "/api/v2/engagements/",    # Lista de engagements
    ]
    
    headers = {'Authorization': f"Token {config['defectdojo']['api_key']}"}
    
    for endpoint in endpoints:
        try:
            url = f"{config['defectdojo']['url']}{endpoint}"
            resposta = requests.get(url, headers=headers, verify=False, timeout=5)
            
            if resposta.status_code == 200:
                dados = resposta.json()
                
                if endpoint == "/api/v2/users/current/":
                    print(f"✅ Conexão OK! Usuário: {dados.get('username', 'N/A')}")
                    print(f"📧 Email: {dados.get('email', 'N/A')}")
                elif endpoint == "/api/v2/engagements/":
                    eng_count = dados.get('count', 0)
                    print(f"📁 Engagements: {eng_count} disponíveis")
                elif endpoint == "/api/v2/users/":
                    user_count = dados.get('count', 0)
                    print(f"👥 Usuários: {user_count} no sistema")
                
                print(f"🌐 Endpoint testado: {endpoint}")
                print(f"📊 Status: {resposta.status_code}")
                return True
                
        except Exception as e:
            continue
    
    print("❌ Não foi possível conectar a nenhum endpoint")
    print("💡 Verifique:")
    print("  1. DefectDojo está rodando? (docker-compose ps)")
    print("  2. API key está correta?")
    print("  3. URL está correta?")
    return False

# ========== LISTAR VULNERABILIDADES ==========
def listar_vulnerabilidades_criticas(config):
    """Lista vulnerabilidades CRÍTICAS do engagement - VERSÃO CORRIGIDA 2.0"""
    print("🚨 DEBUG: Função listar_vulnerabilidades_criticas CHAMADA!")  # ← ADICIONAR
    print("\n🔍 Buscando vulnerabilidades CRÍTICAS...")
    print("\n🔍 Buscando vulnerabilidades CRÍTICAS...")
    
    url = f"{config['defectdojo']['url']}/api/v2/findings/"
    headers = {
        'Authorization': f"Token {config['defectdojo']['api_key']}"
    }
    
    # Parâmetros: críticas, ativas, do seu engagement
    params = {
        'severity': 'Critical',
        'active': 'true',
        'engagement': config['defectdojo']['engagement_id'],
        'limit': 20,
        'prefetch': 'endpoints'  # Isso pode não funcionar como esperado
    }
    
    try:
        resposta = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            findings = dados.get('results', [])
            
            if findings:
                print(f"🎯 Encontradas {len(findings)} vulnerabilidades CRÍTICAS:")
                print("=" * 80)
                
                # PRIMEIRO: Buscar endpoints separadamente
                endpoints_url = f"{config['defectdojo']['url']}/api/v2/endpoints/"
                endpoints_resp = requests.get(endpoints_url, headers=headers, verify=False, timeout=5)
                endpoints_map = {}
                
                if endpoints_resp.status_code == 200:
                    endpoints_data = endpoints_resp.json()
                    for endpoint in endpoints_data.get('results', []):
                        endpoints_map[endpoint['id']] = endpoint
                
                for i, finding in enumerate(findings, 1):
                    # Extrair informações básicas
                    title = finding.get('title', 'Sem título')[:70]
                    finding_id = finding.get('id', 'N/A')
                    cve = finding.get('cve', 'Sem CVE')
                    
                    # Tratar endpoints (pode ser lista de IDs ou objetos)
                    endpoint_info = "N/A"
                    endpoints = finding.get('endpoints', [])
                    
                    if endpoints:
                        if isinstance(endpoints[0], dict):
                            # Já tem objetos completos
                            endpoint_obj = endpoints[0]
                            endpoint_info = endpoint_obj.get('host', 'N/A')
                            if endpoint_obj.get('port'):
                                endpoint_info += f":{endpoint_obj.get('port')}"
                        else:
                            # São IDs numéricos [1, 2, 3]
                            endpoint_ids = endpoints
                            if endpoint_ids and endpoint_ids[0] in endpoints_map:
                                endpoint_obj = endpoints_map[endpoint_ids[0]]
                                endpoint_info = endpoint_obj.get('host', 'N/A')
                                if endpoint_obj.get('port'):
                                    endpoint_info += f":{endpoint_obj.get('port')}"
                    
                    # Status
                    is_active = finding.get('active', False)
                    status = "ACTIVE" if is_active else "INACTIVE"
                    severity = finding.get('severity', 'Critical')
                    
                    # Exibir formatado
                    print(f"{i:2d}. ID: {finding_id} | {status} | {severity}")
                    print(f"    📛 {title}")
                    
                    if cve != 'Sem CVE':
                        print(f"    🎯 CVE: {cve}")
                    
                    print(f"    🌐 Host: {endpoint_info}")
                    
                    # Mostrar se tem patch disponível
                    if finding.get('fix_available'):
                        print(f"    ✅ Patch disponível: Sim")
                    
                    # Mostrar data de publicação
                    publish_date = finding.get('publish_date')
                    if publish_date:
                        print(f"    📅 Publicado: {publish_date}")
                    
                    print(f"    🔗 URL: {config['defectdojo']['url']}/finding/{finding_id}")
                    print("-" * 80)
                    
                print(f"\n📊 Resumo: {len(findings)} vulnerabilidades críticas encontradas")
                
            else:
                print("📭 Nenhuma vulnerabilidade CRÍTICA encontrada.")
                print(f"\n💡 Engagement ID atual: {config['defectdojo']['engagement_id']}")
                print("   Para listar TODOS os findings (de todos engagements):")
                print(f"   curl -H 'Authorization: Token {config['defectdojo']['api_key'][:10]}...' \\")
                print(f"     '{config['defectdojo']['url']}/api/v2/findings/?severity=Critical'")
                
        else:
            print(f"❌ Erro na API: {resposta.status_code}")
            print(f"📄 Resposta: {resposta.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()  # Mostra detalhes do erro
# ========== BULK UPDATE ==========
def bulk_update_findings(config):
    """Atualiza múltiplos findings de uma vez"""
    print("\n🔄 Bulk update de findings...")
    print("⚠️  Esta funcionalidade ainda está em desenvolvimento")
    print("\n📋 Funcionalidades planejadas:")
    print("  1. Atualizar status para 'Mitigated'")
    print("  2. Adicionar notas padronizadas")
    print("  3. Fechar findings antigos")
    print("  4. Exportar relatório")
    
    # TODO: Implementar lógica de bulk update
    print("\n📝 Para agora, use a interface web do DefectDojo:")
    print(f"   {config['defectdojo']['url']}/finding")

# ========== IMPORTAR SCAN ==========
def importar_scan_nmap(config):
    """Importa arquivo de scan NMAP para o DefectDojo"""
    print("\n📤 Importando scan NMAP...")
    print("⚠️  Esta funcionalidade ainda está em desenvolvimento")
    
    # TODO: Implementar importação de scan
    print("\n📋 Como usar manualmente:")
    print("  1. Gere XML do NMAP: sudo nmap -sS -sV -oX scan.xml 192.168.15.0/24")
    print("  2. Use a API diretamente:")
    print(f"     curl -X POST -H 'Authorization: Token {config['defectdojo']['api_key'][:10]}...' \\")
    print(f"       -F 'engagement={config['defectdojo']['engagement_id']}' \\")
    print(f"       -F 'scan_type=Nmap Scan' \\")
    print(f"       -F 'file=@scan.xml' \\")
    print(f"       {config['defectdojo']['url']}/api/v2/import-scan/")

# ========== MENU PRINCIPAL ==========
def mostrar_menu():
    """Exibe menu de opções"""
    print("\n" + "="*50)
    print("🛡️  SCRIPT BLUETEAM - DEFECTDOJO")
    print("="*50)
    print("1. Testar conexão com API")
    print("2. Listar vulnerabilidades CRÍTICAS")
    print("3. Bulk update de findings")
    print("4. Importar scan NMAP")
    print("5. Sair")
    print("="*50)
    
    try:
        opcao = input("Escolha uma opção (1-5): ").strip()
        return opcao
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
        return '5'
    except EOFError:
        print("\n\n👋 Até logo!")
        return '5'

# ========== PROGRAMA PRINCIPAL ==========
def main():
    print("🔄 Inicializando Script Blueteam...")
    
    # Carregar configuração
    config = carregar_configuracao()
    if not config:
        print("❌ Não é possível continuar sem configuração.")
        return
    
    # Loop principal
    while True:
        opcao = mostrar_menu()
        
        if opcao == '1':
            testar_conexao(config)
        elif opcao == '2':
            listar_vulnerabilidades_criticas(config)
        elif opcao == '3':
            bulk_update_findings(config)
        elif opcao == '4':
            importar_scan_nmap(config)
        elif opcao == '5':
            print("\n👋 Saindo... Até a próxima!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")
        
        if opcao != '5':
            input("\n⏎ Pressione Enter para continuar...")

if __name__ == "__main__":
    main()

    #Testando a linha 277 para ver se o Commit vai funcionar corretamente.  




    ##