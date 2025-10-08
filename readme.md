Sistema de Conciliação de Fornecedores Itaminas

Automação profissional para conciliação contábil-financeira entre módulos do sistema Protheus, implementada com Python e Playwright.


FUNCIONALIDADES

Automação completa do sistema Protheus
Extração de relatórios financeiros e contábeis
Processamento de dados com SQLite
Geração de planilha consolidada com diferenças priorizadas
Sistema de logging estruturado em terminal e arquivo
Envio automático de e-mails com resultados
Organização modular de código
Configurações externas com dotenv
Tratamento robusto de exceções


TECNOLOGIAS UTILIZADAS

Python 3.10+ (principal)
Playwright (automação web do Protheus)
SQLite (banco de dados para processamento)
Pandas (manipulação de dados)
OpenPyXL (geração de planilhas Excel)
Jinja2 (templates de e-mail)
Python-Dotenv (gerenciamento de variáveis de ambiente)
Logging (rastreamento de execução)


INSTALAÇÃO E PRÉ-REQUISITOS

Python 3.10 ou superior

Git (para clonar o repositório)

Acesso ao sistema Protheus da Itaminas


1️⃣ CLONE O REPOSITÓRIO:

git clone <url-do-repositorio>
cd itaminas-conciliacao


2️⃣ CRIE E ATIVE UM AMBIENTE VIRTUAL:

python -m venv venv

venv\Scripts\activate


3️⃣ INSTALE AS DEPENDÊNCIAS E O PLAYWRIGHT:

pip install -r requirements.txt
playwright install 


SAÍDA DO SISTEMA

Banco de dados SQLite em /data/database.db

Planilha consolidada em /results/CONCILIACAO_<data>.xlsx

Logs detalhados em /logs/conciliacao_<timestamp>.log



CONFIGURAÇÃO DE E-MAIL

O sistema envia e-mails automáticos via SMTP. Configure no arquivo settings.py:

python
SMTP = {
    "enabled": True,
    "host": "smtp.gmail.com",
    "port": 587,
    "from": "seu_email@dominio.com",
    "password": "sua_senha",
    "template": "templates/email_conciliacao.html",
    "logo": "templates/logo.png"
}


PERIODICIDADE DE EXECUÇÃO

O sistema é configurado para executar automaticamente nos dias 20 e último dia útil de cada mês, a partir das 7h.


FLUXO DE PROCESSAMENTO

Login automático no Protheus

Extração de relatórios financeiros (Títulos a Pagar)

Extração de relatórios contábeis (Balancete)

Processamento e cruzamento de dados

Geração de planilha consolidada

Envio de e-mail com resultados


GERANDO EXE.

build.bat

EXECUTANDO DIST 
cd C:\Users\dev\OneDrive\Documentos\Repositórios\itaminas-conciliacao-fornecedores\dist
itaminas-conciliacao.exe