"""
Configurações do Sistema de Conciliação de Fornecedores
Arquivo: settings.py
Descrição: Configurações globais, constantes e parâmetros do sistema
Desenvolvido por: DCLICK
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta  
from dotenv import load_dotenv

# =============================================================================
# CONFIGURAÇÃO DO AMBIENTE - PARA PYINSTALLER E DESENVOLVIMENTO
# =============================================================================

def setup_environment():
    """
    Configura o ambiente para carregar o .env corretamente tanto no 
    desenvolvimento quanto no executável PyInstaller
    """
    if getattr(sys, 'frozen', False):
        # Se está rodando como executável PyInstaller
        # O .env está no mesmo diretório do executável, não no _MEIPASS
        base_path = Path(sys.executable).parent
        env_path = base_path / '.env'
        print(f"🔧 Modo: Executável PyInstaller")
        print(f"📁 Diretório do executável: {base_path}")
    else:
        # Se está rodando como script
        base_path = Path(__file__).resolve().parent.parent
        env_path = base_path / '.env'
        print(f"🔧 Modo: Desenvolvimento")
        print(f"📁 Diretório do projeto: {base_path}")
    
    # Carregar .env
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ .env carregado de: {env_path}")
        
        # Verificar se as variáveis foram carregadas
        test_vars = ['USUARIO', 'BASE_URL']
        for var in test_vars:
            value = os.getenv(var)
            print(f"   {var}: {'✅' if value else '❌'} {'***' if var == 'USUARIO' and value else value}")
        
        return True
    else:
        print(f"❌ .env NÃO encontrado em: {env_path}")
        print(f"📁 Conteúdo do diretório:")
        try:
            for item in base_path.iterdir():
                print(f"   - {item.name}")
        except Exception as e:
            print(f"   Erro ao listar diretório: {e}")
        return False

# Executar a configuração do ambiente
env_loaded = setup_environment()

class Settings:
    """
    Classe principal de configurações do sistema.
    Centraliza todas as constantes, paths e parâmetros de configuração.
    """
    
    # =========================================================================
    # CONFIGURAÇÕES DE DIRETÓRIOS E PATHS BASE
    # =========================================================================
    
    # Diretório base depende do modo de execução
    if getattr(sys, 'frozen', False):
        BASE_DIR = Path(sys.executable).parent  # Diretório do executável
    else:
        BASE_DIR = Path(__file__).resolve().parent.parent  # Diretório do projeto

    # =========================================================================
    # DADOS SENSÍVEIS (carregados de variáveis de ambiente)
    # =========================================================================
    
    USUARIO = os.getenv("USUARIO", "")              # Usuário do sistema Protheus
    SENHA = os.getenv("SENHA", "")                  # Senha do sistema Protheus
    BASE_URL = os.getenv("BASE_URL", "")            # URL base do sistema Protheus
    WEB_AGENT_PATH = (r"C:\Users\rpa.dclick\Desktop\PROTHEUS DEV.lnk")
    
    # =========================================================================
    # CONFIGURAÇÕES DE PLANILHAS E ARQUIVOS
    # =========================================================================
    
    CAMINHO_PLS = os.getenv("CAMINHO_PLANILHAS", "")  # Caminho para as planilhas
    PLS_FINANCEIRO = os.getenv("PLANILHA_FINANCEIRO", "")  # Nome da planilha financeira
    PLS_MODELO_1 = os.getenv("PLANILHA_MODELO_1", "")     # Nome da planilha modelo 1
    
    # Configurações de fornecedores
    COLUNAS_CONTAS_ITENS = os.getenv("FORNECEDOR_NACIONAL", "ctbr140.xlsx")    # Fornecedor nacional
    COLUNAS_ADIANTAMENTO = os.getenv("ADIANTAMENTO_NACIONAL", "ctbr100.xlsx")  # Adiantamento nacional

    # =========================================================================
    # DIRETÓRIOS DO SISTEMA
    # =========================================================================
    
    DATA_DIR = BASE_DIR / "data"          # Diretório para armazenamento de dados
    LOGS_DIR = BASE_DIR / "logs"          # Diretório para arquivos de log
    RESULTS_DIR = BASE_DIR / "results"    # Diretório para resultados e relatórios
    DB_PATH = DATA_DIR / "database.db"    # Caminho para o banco de dados
    PARAMETERS_DIR = BASE_DIR / "parameters.json"  # Diretório para parâmetros do sistema

    # Paths para download e resultados
    DOWNLOAD_PATH = DATA_DIR 
    RESULTS_PATH = RESULTS_DIR 
    
    # Data base para processamento (formato: DD/MM/AAAA)
    DATA_BASE = datetime.now().strftime("%d/%m/%Y")

    # =========================================================================
    # CONFIGURAÇÕES DE BANCO DE DADOS (TABELAS)
    # =========================================================================
    
    TABLE_FINANCEIRO = "financeiro"       # Tabela para dados financeiros
    TABLE_MODELO1 = "modelo1"             # Tabela para dados do modelo 1
    TABLE_CONTAS_ITENS = "contas_itens"   # Tabela para contas e itens
    TABLE_ADIANTAMENTO = "adiantamento"   # Tabela para adiantamentos
    TABLE_RESULTADO = "resultado"         # Tabela para resultados do processamento
    TABLE_RESULTADO_ADIANTAMENTO = "resultado_adiantamento"  # Tabela para resultados de adiantamentos
    
    # =========================================================================
    # CONFIGURAÇÕES DE TEMPO E DELAYS
    # =========================================================================
    
    TIMEOUT = 30000      # Timeout para operações (30 segundos)
    DELAY = 0.5          # Delay entre operações (0.5 segundos)
    SHUTDOWN_DELAY = 3   # Delay para desligamento (3 segundos)
    
    # =========================================================================
    # CONFIGURAÇÕES DO NAVEGADOR (BROWSER)
    # =========================================================================
    
    HEADLESS = False  # Executar navegador em modo visível para debug
    
    # =========================================================================
    # CONFIGURAÇÕES DE EMAIL
    # =========================================================================
    
    # Lista de destinatários por tipo de email
    EMAILS = {
        "success": ["andre.rodrigues@dclick.com.br"],  # Destinatários para emails de sucesso
        "error": ["andre.rodrigues@dclick.com.br"]     # Destinatários para emails de erro
    }

    PASSWORD = os.getenv("PASSWORD", "") 
    
    # Configurações SMTP para envio de emails
    SMTP = {
        "enabled": True,                       # Habilitar/desabilitar envio de emails
        "host": "smtp.gmail.com",              # Servidor SMTP
        "port": 587,                           # Porta do servidor SMTP
        "from": "suporte@dclick.com.br",       # Remetente dos emails
        "password": PASSWORD,                  # Senha do email remetente
        "template": "templates/email_conciliação.html",  # Template HTML para emails
        "logo": "https://www.dclick.com.br/themes/views/web/assets/logo.svg"  # Logo para emails
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
        Garante que todos os diretórios necessários existem e valida as configurações.
        """
        # Criar diretórios se não existirem
        self._create_directories()
        
        # Validar variáveis críticas (mas não falhar imediatamente)
        self._validate_required_vars()
        
        # Log das configurações carregadas
        self._log_loaded_settings()

    def _create_directories(self):
        """Cria todos os diretórios necessários para o sistema."""
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        os.makedirs(self.RESULTS_DIR, exist_ok=True)
        print("✅ Diretórios do sistema verificados/criados")

    def _validate_required_vars(self):
        """Valida se as variáveis obrigatórias estão presentes e corretas."""
        required_vars = {
            'USUARIO': self.USUARIO,
            'SENHA': self.SENHA, 
            'BASE_URL': self.BASE_URL,
            'CAMINHO_PLANILHAS': self.CAMINHO_PLS,
            'PLANILHA_FINANCEIRO': self.PLS_FINANCEIRO,
            'PLANILHA_MODELO_1': self.PLS_MODELO_1
        }
        
        missing_vars = []
        for var_name, var_value in required_vars.items():
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            error_msg = f"Variáveis de ambiente obrigatórias não carregadas: {', '.join(missing_vars)}"
            print(f"❌ {error_msg}")
            # Não levanta exceção imediatamente, apenas registra o erro
            # raise ValueError(error_msg)

    def _log_loaded_settings(self):
        """Registra as configurações carregadas (sem dados sensíveis)."""
        print("=" * 50)
        print("CONFIGURAÇÕES CARREGADAS:")
        print(f"✅ USUARIO: {'***' if self.USUARIO else '❌ NÃO CARREGADO'}")
        print(f"✅ SENHA: {'***' if self.SENHA else '❌ NÃO CARREGADO'}")
        print(f"✅ BASE_URL: {self.BASE_URL if self.BASE_URL else '❌ NÃO CARREGADO'}")
        print(f"✅ CAMINHO_PLS: {self.CAMINHO_PLS if self.CAMINHO_PLS else '❌ NÃO CARREGADO'}")
        print(f"✅ PLANILHA_FINANCEIRO: {self.PLS_FINANCEIRO if self.PLS_FINANCEIRO else '❌ NÃO CARREGADO'}")
        print(f"✅ PLANILHA_MODELO_1: {self.PLS_MODELO_1 if self.PLS_MODELO_1 else '❌ NÃO CARREGADO'}")
        print(f"✅ DATA_BASE: {self.DATA_BASE}")
        print(f"✅ HEADLESS: {self.HEADLESS}")
        print("=" * 50)

# Instância global para importação
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Erro crítico ao inicializar Settings: {e}")
    # Cria uma instância básica para evitar falha completa
    settings = None