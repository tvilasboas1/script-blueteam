#!/usr/bin/env python3
"""
Script de Análise de Vulnerabilidades - DefectDojo
Versão: 2.1 - Corrigido e Simplificado
"""
from datetime import datetime
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
        print(f"✅ Configuração carregada de: {config_path}")
        
        # Mostrar configuração (ocultando API key)
        api_key = config['defectdojo']['api_key']
        masked_key = api_key[:8] + "..." + api_key[-8:] if len(api_key) > 16 else "***"
        print(f"   URL: {config['defectdojo']['url']}")
        print(f"   API Key: {masked_key}")
        print(f"   Engagement ID: {config['defectdojo']['engagement_id']}")
        
        return config
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {config_path}")
        print("💡 Crie o arquivo Config/DefectDojo.json")
        return None
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None

# ========== TESTE DE CONEXÃO ==========
def testar_conexao(config):
    """Testa conexão com API do DefectDojo"""
    print("\n🔗 Testando conexão com API...")
    
    url = f"{config['defectdojo']['url']}/api/v2/findings/"
    headers = {'Authorization': f"Token {config['defectdojo']['api_key']}"}
    params = {'limit': 1}
    
    try:
        resposta = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            print(f"✅ Conexão OK!")
            print(f"📊 Total de findings: {dados.get('count', 0)}")
            print(f"🌐 API: {config['defectdojo']['url']}")
            return True
        else:
            print(f"❌ Erro {resposta.status_code}")
            print(f"💡 Mensagem: {resposta.text[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

# ========== LISTAR VULNERABILIDADES ==========
def listar_vulnerabilidades_criticas(config):
    """Lista vulnerabilidades CRÍTICAS"""
    print("\n🔍 Buscando vulnerabilidades CRÍTICAS...")
    
    url = f"{config['defectdojo']['url']}/api/v2/findings/"
    headers = {'Authorization': f"Token {config['defectdojo']['api_key']}"}
    
    params = {
        'severity': 'Critical',
        'active': 'true',
        'engagement': config['defectdojo']['engagement_id'],
        'limit': 10
    }
    
    try:
        resposta = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            findings = dados.get('results', [])
            
            if findings:
                print(f"\n🎯 {len(findings)} VULNERABILIDADES CRÍTICAS ENCONTRADAS:")
                print("=" * 80)
                for i, finding in enumerate(findings, 1):
                    print(f"{i:2d}. [{finding.get('id')}] {finding.get('title')}")
                    print(f"     CVE: {finding.get('cve', 'N/A')}")
                    print(f"     Status: {'ACTIVE' if finding.get('active') else 'INACTIVE'}")
                    print(f"     Severity: {finding.get('severity')}")
                    print()
            else:
                print("📭 Nenhuma vulnerabilidade crítica encontrada.")
        else:
            print(f"❌ Erro {resposta.status_code}: {resposta.text[:100]}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

# ========== BULK UPDATE CORRIGIDO ==========
def bulk_update_findings(config):
    """Atualiza múltiplos findings - VERSÃO CORRIGIDA"""
    print("\n🔄 Bulk Update de Findings")
    print("="*50)
    
    # Buscar findings
    print("🔍 Buscando findings ativos...")
    url = f"{config['defectdojo']['url']}/api/v2/findings/"
    headers = {'Authorization': f"Token {config['defectdojo']['api_key']}"}
    
    params = {
        'active': 'true',
        'engagement': config['defectdojo']['engagement_id'],
        'limit': 20  # Aumentei para 20
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Erro ao buscar findings: {response.status_code}")
            return
        
        findings = response.json().get('results', [])
        
        if not findings:
            print("📭 Nenhum finding ativo encontrado.")
            return
        
        print(f"📊 Encontrados {len(findings)} findings ativos")
        
        # Menu
        print("\n🎯 O que deseja fazer?")
        print("1. Marcar como 'Mitigated' (com nota)")
        print("2. Marcar como 'Fixed' (corrigido)")
        print("3. Fechar findings (active=False)")
        print("4. Voltar ao menu")
        
        opcao = input("\nEscolha (1-4): ").strip()
        
        if opcao == '4':
            return
        
        # Processar
        atualizados = 0
        errors = 0
        
        for i, finding in enumerate(findings, 1):
            finding_id = finding['id']
            
            if opcao == '1':  # Mitigated
                update_data = {
                    "status": "Mitigated",
                    "notes": f"Mitigado via script em {datetime.now().date()}",
                    "active": False
                }
            elif opcao == '2':  # Fixed
                update_data = {
                    "status": "Fixed", 
                    "active": False
                }
            elif opcao == '3':  # Fechar
                update_data = {"active": False}
            else:
                print("❌ Opção inválida")
                return
            
            # Atualizar
            update_url = f"{config['defectdojo']['url']}/api/v2/findings/{finding_id}/"
            try:
                update_response = requests.patch(
                    update_url, 
                    headers=headers, 
                    json=update_data, 
                    verify=False,
                    timeout=5
                )
                
                if update_response.status_code in [200, 204]:
                    atualizados += 1
                    print(f"✅ {atualizados}/{len(findings)} - ID {finding_id}")
                else:
                    errors += 1
                    
            except Exception as e:
                errors += 1
        
        print(f"\n{'='*50}")
        print(f"🎉 CONCLUSÃO:")
        print(f"✅ {atualizados} findings atualizados")
        print(f"❌ {errors} erros")
        
    except Exception as e:
        print(f"❌ Erro no bulk update: {str(e)}")

# ========== IMPORTAR SCAN NMAP ==========
def importar_scan_nmap(config):
    """Importa arquivo de scan NMAP"""
    print("\n📤 Importar Scan NMAP")
    print("="*50)
    
    # Pedir caminho do arquivo
    xml_path = input("Caminho do arquivo XML do NMAP: ").strip()
    
    if not xml_path:
        print("❌ Caminho vazio. Cancelado.")
        return
    
    if not Path(xml_path).exists():
        print(f"❌ Arquivo não existe: {xml_path}")
        return
    
    print(f"📁 Arquivo: {xml_path}")
    print("📤 Enviando para DefectDojo...")
    
    # Aqui você implementaria o upload real
    print("⚠️  Funcionalidade em desenvolvimento")
    print(f"💡 Use: curl -X POST {config['defectdojo']['url']}/api/v2/import-scan/")

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
        opcao = input("Escolha (1-5): ").strip()
        return opcao
    except:
        return '5'

# ========== PROGRAMA PRINCIPAL ==========
def main():
    print("\n" + "="*50)
    print("🔄 Inicializando Script Blueteam DefectDojo")
    print("="*50)
    
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