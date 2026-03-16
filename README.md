# Automação de Gestão de Vulnerabilidades (Blue Team)

![Status](https://img.shields.io/badge/Status-Produção-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![DefectDojo](https://img.shields.io/badge/Integração-DefectDojo-orange)

Este projeto foi desenvolvido como parte da Residência Tecnológica em Cibersegurança da **RNP** (Rede Nacional de Ensino e Pesquisa) e aplicado no ambiente corporativo da **Universidade Federal da Bahia (UFBA)**.

## Objetivo Corporativo
O script atua como uma ponte automatizada no processo de Gestão de Vulnerabilidades. Ele ingere resultados brutos de scanners de rede (como o Nmap), processa os dados e os injeta automaticamente via API na plataforma centralizada de gestão (DefectDojo). 

Isso resulta em:
- **Redução de esforço manual** em análise e digitação.
- **Padronização de achados** e eliminação de falhas humanas.
- Criação de um baseline inicial de segurança, alinhado às normas **NIST SP 800-115** e **ISO/IEC 27001**.
- Mitigação baseada em risco real da superfície de ataque.

## Estrutura do Projeto

* `Config/` - Contém as credenciais de API (protegidas) e modelos (`.example`).
* `DefectDojo/` - Scripts core de automação em Python.
* `Scans/` - Diretório de destino para os arquivos XML brutos gerados pelos scanners.
* `Backups/` - Histórico de versões e scripts antigos mantidos por segurança.

## Pré-requisitos
* Sistema Operacional Linux (Debian/Ubuntu recomendado).
* Python 3 instalado.
* DefectDojo rodando (Local via Docker ou Servidor Remoto).
* Biblioteca Python `requests`.
  ```bash
  pip install requests
