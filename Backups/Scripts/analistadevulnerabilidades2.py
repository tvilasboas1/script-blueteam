#!/usr/bin/env python3
"""
Script de Análise de Vulnerabilidades - DefectDojo
Autor: Thiago Boas
Versão: 2.1 - Correções de bugs
"""
from datetime import datetime
import json
import requests
from pathlib import Path
import urllib3
import warnings

# Desabilitar warnings de SSL para ambientes internos
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
     """Testa conexão com API do DefectDojo"""
    print("\n🔗 Testando conexão com DefectDojo...")
    
    headers = {'Authorization': f"Token {config['defectdojo']['api_key']}"}
    
    # CORRIGIDO: URLs sem duplicar /api/v2/
    endpoints = [
        f"{config['defectdojo']['url']}users/",  # ← CORRETO
        f"{config['defectdojo']['url']}",  # ← CORRETO
    ]
    
    for endpoint in endpoints:
        try:
            resposta = requests.get(endpoint, headers=headers, verify=False, timeout=10)
            print(f"📡 Testando: {endpoint}")
            
            if resposta.status_code == 200:
                dados = resposta.json()
                print(f"✅ Conexão OK! Status: {resposta.status_code}")
                print(f"🌐 URL: {config['defectdojo']['url']}")
                
                # Verificar se é a versão 2.x
                if 'count' in dados:
                    print(f"📊 API v2.x detectada - {dados.get('count', 0)} itens")
                return True
            else:
                print(f"⚠️  Status {resposta.status_code} para {endpoint}")
                
        except Exception as e:
            print(f"❌ Erro em {endpoint}: {str(e)}")
            continue
    
    return False
    
    # Se nenhum endpoint funcionar, testar conexão básica
    try:
        # Testar apenas se a URL responde
        base_response = requests.get(config['defectdojo']['url'], verify=False, timeout=5)
        print(f"\n🌐 URL base responde: {base_response.status_code}")
        print("💡 Possíveis problemas:")
        print("  1. URL da API incorreta - verifique se termina com /api/v2/")
        print("  2. API token expirado ou inválido")
        print("  3. DefectDojo não está rodando ou está em port diferente")
    except Exception as e:
        print(f"❌ Não foi possível conectar: {str(e)}")
    
    return False

# ========== LISTAR VULNERABILIDADES ==========
def listar_vulnerabilidades_criticas(config):
    """Lista vulnerabilidades CRÍTICAS do engagement"""
    print("\n🔍 Buscando vulnerabilidades CRÍTICAS...")
    
    url = f"{config['defectdojo']['url']}findings/"  # ← REMOVA /api/v2/ DAQUI
    headers = {'Authorization': f"Token {config['defectdojo']['api_key']}"}
    
    params = {
        'severity': 'Critical',
        'active': 'true',
        'engagement': config['defectdojo']['engagement_id'],
        'limit': 20
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
                    if finding.get('cve'):
                        print(f"     CVE: {finding.get('cve')}")
                    print(f"     Status: {'ACTIVE' if finding.get('active') else 'INACTIVE'}")
                    print(f"     Severity: {finding.get('severity')}")
                    print()
            else:
                print("📭 Nenhuma vulnerabilidade crítica encontrada.")
        else:
            print(f"❌ Erro {resposta.status_code}: {resposta.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

# ========== BULK UPDATE REAL ==========
def bulk_update_findings(config):
    """Atualiza MÚLTIPLOS findings automaticamente - VERSÃO CORRIGIDA"""
    print("\n🔄 Bulk Update de Findings")
    print("="*50)
    
    # 1. BUSCAR FINDINGS
    print("🔍 Buscando findings ativos...")
    update_url = f"{config['defectdojo']['url']}findings/{finding_id}/"
    headers = {'Authorization': f"Token {config['defectdojo']['api_key']}"}
    
    params = {
        'active': 'true',
        'engagement': config['defectdojo']['engagement_id'],
        'limit': 50
    }
    
    response = requests.get(url, headers=headers, params=params, verify=False)
    
    if response.status_code != 200:
        print(f"❌ Erro ao buscar findings: {response.status_code}")
        print(f"Resposta: {response.text[:200]}")
        return
    
    findings = response.json().get('results', [])
    
    if not findings:
        print("📭 Nenhum finding ativo encontrado.")
        return
    
    print(f"📊 Encontrados {len(findings)} findings ativos")
    
    # 2. MENU DE OPÇÕES
    print("\n🎯 O que deseja fazer?")
    print("1. Marcar como 'Mitigated' (com nota)")
    print("2. Marcar como 'Fixed' (corrigido)")
    print("3. Fechar findings antigos (active=False)")
    print("4. Adicionar tag em lote")
    
    try:
        opcao = input("\nEscolha (1-4): ").strip()
    except:
        print("❌ Opção inválida")
        return
    
    # 3. EXECUTAR AÇÃO EM LOTE
    atualizados = 0
    errors = 0
    
    # Para opção 4, pedir a tag
    tag = ""
    if opcao == '4':
        tag = input("Digite a tag a ser adicionada: ").strip()
        if not tag:
            print("❌ Tag não pode ser vazia")
            return
    
    print(f"\n⏳ Processando {len(findings)} findings...")
    
    for i, finding in enumerate(findings, 1):
        finding_id = finding['id']
        title = finding['title'][:50] + "..." if len(finding['title']) > 50 else finding['title']
        
        update_data = {}
        
        if opcao == '1':  # Mitigated
            update_data = {
                "status": "Mitigated",
                "notes": f"Mitigado via script automático em {datetime.now().date()}",
                "active": False,
                "mitigation": "Mitigação aplicada conforme análise de risco"
            }
        elif opcao == '2':  # Fixed
            update_data = {
                "status": "Fixed", 
                "notes": f"Corrigido via script automático em {datetime.now().date()}",
                "active": False,
                "mitigation": "Correção aplicada e validada"
            }
        elif opcao == '3':  # Fechar
            update_data = {"active": False}
        elif opcao == '4':
            current_tags = finding.get('tags', [])
            if tag not in current_tags:
                update_data = {"tags": current_tags + [tag]}
            else:
                print(f"⚠️  Tag '{tag}' já existe no finding {finding_id}")
                continue
        else:
            print("❌ Opção inválida")
            return
        
        # Atualizar finding
        update_url = f"{config['defectdojo']['url']}/api/v2/findings/{finding_id}/"
        try:
            update_response = requests.patch(
                update_url, 
                headers=headers, 
                json=update_data, 
                verify=False,
                timeout=10
            )
            
            if update_response.status_code in [200, 204]:
                atualizados += 1
                if atualizados % 10 == 0:
                    print(f"✅ {atualizados}/{len(findings)} atualizados...")
            else:
                errors += 1
                print(f"⚠️  Erro {update_response.status_code} no finding {finding_id}: {title}")
                print(f"     Resposta: {update_response.text[:100]}")
                
        except Exception as e:
            errors += 1
            print(f"❌ Exceção no finding {finding_id}: {str(e)}")
    
    print(f"\n{'='*50}")
    print(f"🎉 CONCLUSÃO:")
    print(f"✅ {atualizados}/{len(findings)} findings atualizados com sucesso")
    print(f"❌ {errors} erros encontrados")
    if atualizados > 0:
        print(f"📋 Acesse: {config['defectdojo']['url']}/finding")

# ========== IMPORTAR SCAN ==========
def importar_scan_nmap(config):
    """Importa arquivo de scan NMAP para o DefectDojo"""
    print("\n📤 Importando scan NMAP...")
    print("\n📤 Importando scan NMAP...")
    print("⚠️  Esta funcionalidade é complexa. Use o método manual:")
    
    print("\n📋 COMO IMPORTAR MANUALMENTE:")
    print(f"1. Acesse: {config['defectdojo']['url'].replace('/api/v2/', '')}")
    print("2. Vá para o engagement")
    print("3. Clique em 'Import Scan Results'")
    print("4. Selecione 'Nmap Scan' e faça upload do XML")
    
    print("\n💡 Comando curl (avançado):")
    print(f"curl -X POST '{config['defectdojo']['url'].replace('/api/v2/', '')}/api/v2/import-scan/' \\")
    print(f"  -H 'Authorization: Token {config['defectdojo']['api_key'][:20]}...' \\")
    print("  -F 'engagement=1' \\")
    print("  -F 'scan_type=\"Nmap Scan\"' \\")
    print("  -F 'file=@seu_scan.xml'")
    
    # Pedir caminho do arquivo
    xml_file = input("Caminho do arquivo XML do NMAP: ").strip()
    
    if not xml_file or not Path(xml_file).exists():
        print(f"❌ Arquivo não encontrado: {xml_file}")
        return
    
    url = f"{config['defectdojo']['url']}findings/"  # ← REMOVA /api/v2/ DAQUI
    headers = {'Authorization': f"Token {config['defectdojo']['api_key']}"}
    
    files = {
        'file': open(xml_file, 'rb'),
        'engagement': (None, str(config['defectdojo']['engagement_id'])),
        'scan_type': (None, 'Nmap Scan'),
        'verified': (None, 'false'),
        'active': (None, 'true'),
        'minimum_severity': (None, 'Info')
    }
    
    try:
        print("📤 Enviando arquivo...")
        response = requests.post(url, headers=headers, files=files, verify=False)
        
        if response.status_code in [200, 201]:
            print("✅ Scan importado com sucesso!")
            print(f"📋 Resposta: {response.json()}")
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    finally:
        files['file'].close()

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
    print("5. Ver configuração atual")
    print("6. Sair")
    print("="*50)
    
    try:
        opcao = input("Escolha uma opção (1-6): ").strip()
        return opcao
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
        return '6'
    except EOFError:
        print("\n\n👋 Até logo!")
        return '6'

# ========== VER CONFIGURAÇÃO ==========
def ver_configuracao(config):
    """Mostra configuração atual (ocultando API key)"""
    print("\n🔧 Configuração Atual:")
    print("="*50)
    
    if 'defectdojo' in config:
        config_copy = config.copy()
        if 'api_key' in config_copy['defectdojo']:
            api_key = config_copy['defectdojo']['api_key']
            masked_key = api_key[:10] + "..." + api_key[-10:] if len(api_key) > 20 else "***"
            config_copy['defectdojo']['api_key'] = masked_key
        
        print(json.dumps(config_copy, indent=2, ensure_ascii=False))
    else:
        print("❌ Configuração não encontrada")
    
    print("\n📁 Caminho do arquivo config:")
    print(f"   {Path(__file__).parent.parent / 'Config' / 'DefectDojo.json'}")

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
            ver_configuracao(config)
        elif opcao == '6':
            print("\n👋 Saindo... Até a próxima!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")
        
        if opcao != '6':
            input("\n⏎ Pressione Enter para continuar...")

if __name__ == "__main__":
    main()