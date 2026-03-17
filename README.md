# 🛡️ Automação de Gestão de Vulnerabilidades (Blue Team)

![Status](https://img.shields.io/badge/Status-Produção-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![DefectDojo](https://img.shields.io/badge/Integração-DefectDojo-orange)

Este projeto foi desenvolvido como parte da Residência Tecnológica em Cibersegurança da **RNP** (Rede Nacional de Ensino e Pesquisa) para ser e aplicado no ambiente corporativo do **POP-BA** e também da **Universidade Federal da Bahia (UFBA)**.

## 🎯 Objetivo Corporativo
O script atua como uma ponte automatizada no processo de Gestão de Vulnerabilidades. Ele ingere resultados brutos de scanners de rede (como o Nmap), processa os dados e os injeta automaticamente via API na plataforma centralizada de gestão (DefectDojo). 

Isso resulta em:
- **Redução de esforço manual** em análise e digitação.
- **Padronização de achados** e eliminação de falhas humanas.
- Criação de um baseline inicial de segurança, alinhado às normas **NIST SP 800-115** e **ISO/IEC 27001**.
- Mitigação baseada em risco real da superfície de ataque.

## 📁 Estrutura do Projeto

* `Config/` - Contém as credenciais de API (protegidas) e modelos (`.example`).
* `DefectDojo/` - Scripts core de automação em Python.
* `Scans/` - Diretório de destino para os arquivos XML brutos gerados pelos scanners.

---

## ⚙️ Pré-requisitos
* Sistema Operacional Linux (Debian/Ubuntu recomendado).
* Python 3 instalado.
* DefectDojo rodando (Local via Docker ou Servidor Remoto).

---

## 🚀 Guia Passo a Passo (Como Instalar e Usar)

Siga os passos abaixo para colocar a automação para rodar no seu ambiente:

### Passo 1: Download do Projeto
Faça o clone do repositório para a sua máquina e entre na pasta:
```bash
git clone https://github.com/tvilasboas1/script-blueteam.git
cd script-blueteam
```

### Passo 2: Instalar Dependências
Instale a biblioteca de comunicação via API do Python:
```bash
pip install requests
```

### Passo 3: Configurar as Credenciais do DefectDojo 
Copie o arquivo de exemplo para criar o seu arquivo de configuração local:
```bash
cp Config/DefectDojo.json.example Config/DefectDojo.json
```
Edite o arquivo `DefectDojo.json` que você acabou de criar e insira a URL do seu servidor e a sua Chave de API gerada no painel do DefectDojo.

### Passo 4: Gerar um Arquivo de Scan (Exemplo com Nmap)
Para que o script funcione, ele precisa de um arquivo `.xml` com os resultados de uma varredura. Rode o seu scanner e salve o resultado dentro da pasta `Scans/`.

Exemplo de comando Nmap:
```bash
sudo nmap -T4 192.168.0.1/24 -oX Scans/meu_scan_rede.xml
```

### Passo 5: Executar a Automação
Com tudo instalado e configurado, inicie o motor principal:
```bash
python3 DefectDojo/analistadevulnerabilidades.py
```

## 👨‍💻 Autor

**Thiago Santos Vilas Boas** *Analista de Cibersegurança (Blue Team)* - [LinkedIn](https://www.linkedin.com/in/thiago-s-vilas-boas-696107b5/)
- Projeto desenvolvido para a RNP e UFBA.  
