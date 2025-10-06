"""
Configurações do Sistema de Conciliação de Fornecedores
Arquivo: settings.py
Descrição: Configurações globais, constantes e parâmetros do sistema
Desenvolvido por: DCLICK
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta  
from dotenv import load_dotenv

class Settings:
    """
    Classe principal de configurações do sistema.
    Centraliza todas as constantes, paths e parâmetros de configuração.
    """
    
    # =========================================================================
    # CONFIGURAÇÕES DE DIRETÓRIOS E PATHS BASE
    # =========================================================================
    
    # Diretório base do projeto (nível acima do diretório atual)
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Carrega variáveis de ambiente do arquivo .env
    load_dotenv(BASE_DIR / ".env")

    # =========================================================================
    # DADOS SENSÍVEIS (carregados de variáveis de ambiente)
    # =========================================================================
    
    USUARIO = os.getenv("USUARIO")              # Usuário do sistema Protheus
    SENHA = os.getenv("SENHA")                  # Senha do sistema Protheus
    BASE_URL = os.getenv("BASE_URL")            # URL base do sistema Protheus
    WEB_AGENT_PATH = (r"C:\Users\rpa.dclick\Desktop\PROTHEUS DEV.lnk")
    # =========================================================================
    # CONFIGURAÇÕES DE PLANILHAS E ARQUIVOS
    # =========================================================================
    
    CAMINHO_PLS = os.getenv("CAMINHO_PLANILHAS")  # Caminho para as planilhas
    PLS_FINANCEIRO = os.getenv("PLANILHA_FINANCEIRO")  # Nome da planilha financeira
    PLS_MODELO_1 = os.getenv("PLANILHA_MODELO_1")     # Nome da planilha modelo 1
    
    # Configurações de fornecedores
    COLUNAS_CONTAS_ITENS = os.getenv("FORNECEDOR_NACIONAL")    # Fornecedor nacional
    COLUNAS_ADIANTAMENTO = os.getenv("ADIANTAMENTO_NACIONAL")  # Adiantamento nacional

    # =========================================================================
    # DIRETÓRIOS DO SISTEMA
    # =========================================================================
    
    DATA_DIR = BASE_DIR / "data"          # Diretório para armazenamento de dados
    LOGS_DIR = BASE_DIR / "logs"          # Diretório para arquivos de log
    RESULTS_DIR = BASE_DIR / "results"    # Diretório para resultados e relatórios
    DB_PATH = DATA_DIR / "database.db"    # Caminho para o banco de dados
    # UPLOAD_DIR = Path("./uploads/")       # Diretório para uploads de arquivos
    PARAMETERS_DIR = BASE_DIR / "parameters.json"         # Diretório para parâmetros do sistema

    # Paths para download e resultados
    DOWNLOAD_PATH = DATA_DIR 
    RESULTS_PATH = RESULTS_DIR 
    
    # Data base para processamento (formato: DD/MM/AAAA)
    DATA_BASE = datetime.now().strftime("%d/%m/%Y")

    # Criar diretórios se não existirem
    DATA_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)

    # =========================================================================
    # CONFIGURAÇÕES DE BANCO DE DADOS (TABELAS)
    # =========================================================================
    
    TABLE_FINANCEIRO = "financeiro"       # Tabela para dados financeiros
    TABLE_MODELO1 = "modelo1"             # Tabela para dados do modelo 1
    TABLE_CONTAS_ITENS = "contas_itens"   # Tabela para contas e itens
    TABLE_ADIANTAMENTO = "adiantamento"   # Tabela para adiantamentos
    TABLE_RESULTADO = "resultado"         # Tabela para resultados do processamento
    TABLE_RESULTADO_ADIANTAMENTO = "resultado_adiantamento"  # NOVA: Tabela para resultados de adiantamentos
    # =========================================================================
    # CONFIGURAÇÕES DE TEMPO E DELAYS
    # =========================================================================
    
    TIMEOUT = 30000      # Timeout para operações (30 segundos)
    DELAY = 0.5          # Delay entre operações (0.5 segundos)
    SHUTDOWN_DELAY = 3   # Delay para desligamento (3 segundos)
    
    # =========================================================================
    # CONFIGURAÇÕES DO NAVEGADOR (BROWSER)
    # =========================================================================
    
    HEADLESS = True  # Executar navegador em modo headless (sem interface)
    
    # =========================================================================
    # CONFIGURAÇÕES DE EMAIL
    # =========================================================================
    
    # Lista de destinatários por tipo de email
    EMAILS = {
        "success": ["andre.rodrigues@dclick.com.br"],  # Destinatários para emails de sucesso
        "error": ["andre.rodrigues@dclick.com.br"]     # Destinatários para emails de erro
    }

    PASSWORD = os.getenv("PASSWORD") 
    # Configurações SMTP para envio de emails
    SMTP = {
        "enabled": True,                       # Habilitar/desabilitar envio de emails
        "host": "smtp.gmail.com",           # Servidor SMTP
        "port": 587,                            # Porta do servidor SMTP
        "from": "suporte@dclick.com.br",                           # Remetente dos emails
        "password": PASSWORD,                    # Senha do email remetente
        "template": "templates/email_conciliação.html",  # Template HTML para emails
        "logo": "https://www.dclick.com.br/themes/views/web/assets/logo.svg"            # Logo para incorporar nos emails
    }

    # =========================================================================
    # CONFIGURAÇÕES DE PLANILHAS E PROCESSAMENTO
    # =========================================================================
    
    # Fornecedores a serem excluídos do processamento
    FORNECEDORES_EXCLUIR = ['NDF', 'PA']  
    
    # Data de referência para processamento (último dia do mês anterior)
    DATA_REFERENCIA = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%d/%m/%Y") 

    # =========================================================================
    # MAPEAMENTO DE COLUNAS DAS PLANILHAS
    # =========================================================================
    
    # Planilha Financeira (finr150.xlsx)
    COLUNAS_FINANCEIRO = {
        'Codigo-Nome do Fornecedor': 'fornecedor',
        'Prf-Numero Parcela': 'titulo', 
        'Tp': 'tipo_titulo',
        'Data de Emissao': 'data_emissao',
        'Data de Vencto': 'data_vencimento',
        'Valor Original': 'valor_original',
        'Tit Vencidos Valor nominal': 'tit_vencidos_valor_nominal',
        'Titulos a vencer Valor nominal': 'titulos_a_vencer_valor_nominal',
        'Natureza': 'situacao',
        'Porta- dor': 'centro_custo'
    }

    # Planilha Modelo 1 (ctbr040.xlsx)
    COLUNAS_MODELO1 = {
        'conta_contabil': 'Conta',
        'descricao_conta': 'Descricao',
        'saldo_anterior': 'Saldo anterior',
        'debito': 'Debito',
        'credito': 'Credito',
        'movimento_periodo': 'Mov  periodo',
        'saldo_atual': 'Saldo atual'
    }

    # Planilha Fornecedor Nacional (ctbr140.txt)
    COLUNAS_CONTAS_ITENS = {
        'conta_contabil': 'Codigo',
        'descricao_item': 'Descricao',
        'codigo_fornecedor': 'Codigo.1',
        'descricao_fornecedor': 'Descricao.1',
        'saldo_anterior': 'Saldo anterior',
        'debito': 'Debito',
        'credito': 'Credito',
        'movimento_periodo': 'Movimento do periodo',
        'saldo_atual': 'Saldo atual'
    }

    # Planilha Adiantamento Nacional (ctbr100.txt)
    COLUNAS_ADIANTAMENTO = {
        'conta_contabil': 'Codigo',
        'descricao_item': 'Descricao',
        'codigo_fornecedor': 'Codigo.1',
        'descricao_fornecedor': 'Descricao.1',
        'saldo_anterior': 'Saldo anterior',
        'debito': 'Debito',
        'credito': 'Credito',
        'movimento_periodo': 'Movimento do periodo',
        'saldo_atual': 'Saldo atual'
    }

    def __init__(self):
        """
        Inicializador da classe Settings.
        Garante que todos os diretórios necessários existam.
        """
        # Criar diretórios se não existirem
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        os.makedirs(self.RESULTS_DIR, exist_ok=True)