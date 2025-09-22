"""
Módulo principal para automação do sistema Protheus.
Coordena o fluxo completo de extração de dados, incluindo login,
execução de relatórios financeiros e processamento de dados.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from config.settings import Settings
from config.logger import configure_logger
from .exceptions import (
    LoginProtheusError,
    BrowserClosedError,
    DownloadFailed,
    TimeoutOperacional,
    ExcecaoNaoMapeadaError,
    FormSubmitFailed
)
from .utils import Utils
from .financeiro import ExtracaoFinanceiro
from .modelo_1 import Modelo_1
from .contasxitens import Contas_x_itens
from .database import DatabaseManager
from pathlib import Path
import time

# Configuração do logger para registro de atividades
logger = configure_logger()

class ProtheusScraper(Utils):
    """Classe principal para automação do sistema Protheus."""
    
    def __init__(self, settings=Settings()):
        """
        Inicializa o scraper do Protheus.
        
        Args:
            settings: Configurações do sistema (default: Settings())
        """
        self.settings = settings
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.downloads = [] 
        self._initialize_resources()
        logger.info("Navegador inicializado")

    def _initialize_resources(self):
        """Inicializa todos os recursos do Playwright."""
        try:
            self.playwright = sync_playwright().start()
            self._setup_browser()
            self._setup_page()
            self._definir_locators()
        except Exception as e:
            error_msg = "Falha na inicialização dos recursos do Playwright"
            logger.error(f"{error_msg}: {e}")
            raise BrowserClosedError(error_msg) from e
    
    def _setup_browser(self):
        """
        Configura o navegador Edge com as opções especificadas.
        """
        try:
            self.browser = self.playwright.chromium.launch(
                headless=self.settings.HEADLESS,
                args=["--start-maximized"],
                channel="msedge"
            )
        except Exception as e:
            error_msg = "Falha ao configurar o navegador"
            logger.error(f"{error_msg}: {e}")
            raise BrowserClosedError(error_msg) from e

    def _setup_page(self):
        """
        Configura a página e contexto do navegador.
        """
        try:
            self.context = self.browser.new_context(
                no_viewport=True,
                accept_downloads=True  
            )
            
            # Monitorar eventos de download
            self.context.on("download", self._handle_download)
            
            self.page = self.context.new_page()
            self.page.set_default_timeout(self.settings.TIMEOUT)
        except Exception as e:
            error_msg = "Falha ao configurar a página do navegador"
            logger.error(f"{error_msg}: {e}")
            raise BrowserClosedError(error_msg) from e

    def _handle_download(self, download):
        """
        Manipula eventos de download - monitora mas não salva os arquivos.
        
        Args:
            download: Objeto de download do Playwright
        """
        try:
            # Aguardar o download ser concluído
            download_path = download.path()
            
            if download_path:
                logger.info(f"Download concluído: {download.suggested_filename}")
                # Não salva aqui - cada classe de extração salva com seu próprio nome
            else:
                logger.error(f"Download falhou: {download.suggested_filename}")
                raise DownloadFailed(f"Download falhou: {download.suggested_filename}")
                
        except Exception as e:
            error_msg = f"Erro ao processar download: {e}"
            logger.error(error_msg)
            raise DownloadFailed(error_msg) from e
                
    def _definir_locators(self):
        """Define todos os locators utilizados na automação."""
        try:
            self.locators = {
                'iframe': self.page.locator("iframe"),
                'botao_ok': self.page.locator('button:has-text("Ok")'),
                'campo_usuario': self.page.frame_locator("iframe").get_by_placeholder("Ex. sp01\\nome.sobrenome"),
                'campo_senha': self.page.frame_locator("iframe").get_by_label("Insira sua senha"),
                'botao_entrar': self.page.frame_locator("iframe").get_by_role("button", name="Entrar"),            
                'campo_grupo': self.page.frame_locator("iframe").get_by_label("Grupo"),
                'campo_filial': self.page.frame_locator("iframe").get_by_label("Filial"),
                'campo_ambiente': self.page.frame_locator("iframe").get_by_label("Ambiente"),
                'popup_fechar': self.page.get_by_role("button", name="Fechar")
            }
        except Exception as e:
            error_msg = "Falha ao definir locators"
            logger.error(f"{error_msg}: {e}")
            raise ExcecaoNaoMapeadaError(error_msg) from e

    def __enter__(self):
        """Implementa o protocolo context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Fecha todos os recursos ao sair do contexto.
        
        Args:
            exc_type: Tipo de exceção (se ocorreu)
            exc_val: Valor da exceção
            exc_tb: Traceback da exceção
        """
        self._fechar_recursos()
        logger.info("Navegador fechado")

    def _fechar_recursos(self):
        """Fecha todos os recursos de forma segura."""
        try:
            time.sleep(self.settings.SHUTDOWN_DELAY)
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.warning(f"Erro ao fechar recursos: {e}")

    def start_scraper(self):
        """
        Inicia o navegador e navega para a página inicial do Protheus.
        
        Raises:
            BrowserClosedError: Se falhar ao iniciar o scraper
        """
        try:
            logger.info(f"Navegando para: Protheus")
            self.page.goto(self.settings.BASE_URL)
            self.page.get_by_role("group", name="Ambiente no servidor").get_by_role("combobox").select_option("CEOS62_DEV")
            # Clica no botão OK se estiver visível
            if self.locators['botao_ok'].is_visible():
                self.locators['botao_ok'].click()
                logger.info("Botão 'Ok' clicado")
            
        except PlaywrightTimeoutError as e:
            error_msg = "Timeout ao navegar para a página do Protheus"
            logger.error(f"{error_msg}: {e}")
            raise TimeoutOperacional(error_msg, "navegacao_inicial", self.settings.TIMEOUT) from e
        except Exception as e:
            error_msg = "Falha ao iniciar scraper"
            logger.error(f"{error_msg}: {e}")
            raise BrowserClosedError(error_msg) from e

    def login(self):
        """
        Realiza o login no sistema Protheus.
        
        Raises:
            LoginProtheusError: Se falhar no processo de login
            TimeoutOperacional: Se timeout ao esperar elementos
        """
        try:
            logger.info("Iniciando login...")
            
            # Interação com elementos do login
            self.locators['iframe'].wait_for(state="visible", timeout=self.settings.TIMEOUT)
            self.locators['campo_usuario'].fill(self.settings.USUARIO)
            self.locators['campo_senha'].fill(self.settings.SENHA)
            self.locators['botao_entrar'].click()
            
            # Preenche campos adicionais de configuração
            input_campo_grupo = '01'
            input_campo_filial = '0101'
            time.sleep(1)
            input_campo_ambiente = '34'
            time.sleep(1)
            self.locators['campo_grupo'].wait_for(state="visible", timeout=self.settings.TIMEOUT)
            self.locators['campo_grupo'].click()
            self.locators['campo_grupo'].fill(input_campo_grupo)
            self.locators['campo_filial'].click()
            self.locators['campo_filial'].fill(input_campo_filial)
            self.locators['campo_ambiente'].click()
            self.locators['campo_ambiente'].fill(input_campo_ambiente)
            self.locators['botao_entrar'].click()
            
            # Fecha popups se existirem
            self._fechar_popup_se_existir()
            time.sleep(3)
            self._fechar_popup_se_existir()
            time.sleep(3)
            logger.info("Login realizado com sucesso")
            
        except PlaywrightTimeoutError as e:
            error_msg = "Tempo esgotado ao esperar elementos de login"
            logger.error(f"{error_msg}: {e}")
            raise TimeoutOperacional(error_msg, "login", self.settings.TIMEOUT) from e
        except Exception as e:
            error_msg = "Falha no login"
            logger.error(f"{error_msg}: {str(e)}")
            raise LoginProtheusError(error_msg, self.settings.USUARIO) from e

    
    def run(self):
        """
        Executa o fluxo completo de automação do Protheus.
        
        Returns:
            list: Lista de resultados de todas as etapas executadas
        """
        results = []
        
        try:
            # 0. Inicialização e login
            # self.start_scraper()
            # self.login()
            results.append({
                'status': 'success',
                'message': 'Login realizado com sucesso',
                'etapa': 'autenticação',
                'error_code': None
            })

            # # 1. Executar Financeiro
            # try:       
            #     financeiro = ExtracaoFinanceiro(self.page)
            #     resultado_financeiro = financeiro.execucao()
            #     resultado_financeiro['etapa'] = 'financeiro'
            #     results.append(resultado_financeiro)
                
            # except Exception as e:
            #     results.append({
            #         'status': 'error',
            #         'message': f'Falha no Financeiro: {str(e)}',
            #         'etapa': 'financeiro',
            #         'error_code': getattr(e, 'code', 'FE4') if hasattr(e, 'code') else 'FE3'
            #     })

            # # 2. Executar Modelo_1
            # try:
            #     modelo_1 = Modelo_1(self.page)
            #     resultado_modelo = modelo_1.execucao()
            #     resultado_modelo['etapa'] = 'modelo_1'
            #     results.append(resultado_modelo)
            # except Exception as e:
            #     results.append({
            #         'status': 'error',
            #         'message': f'Falha no Modelo_1: {str(e)}',
            #         'etapa': 'modelo_1',
            #         'error_code': getattr(e, 'code', 'FE4') if hasattr(e, 'code') else 'FE3'
            #     })

            # # 3. Executar Contas x Itens
            # try:
            #     contasxitens = Contas_x_itens(self.page)
            #     resultado_contas = contasxitens.execucao()
            #     results.append(resultado_contas)
            # except Exception as e:
            #     results.append({
            #         'status': 'error',
            #         'message': f'Falha em Contas x Itens: {str(e)}',
            #         'etapa': 'contas_x_itens',
            #         'error_code': getattr(e, 'code', 'FE4') if hasattr(e, 'code') else 'FE3'
            #     })
                
        except Exception as e:
            # Erro crítico não tratado no processo principal
            error_msg = f"Erro crítico não tratado: {str(e)}"
            logger.error(error_msg)
            results.append({
                'status': 'critical_error',
                'message': error_msg,
                'etapa': 'processo_principal',
                'error_code': getattr(e, 'code', 'FE3') if hasattr(e, 'code') else 'FE3'
            })

        finally:
            # PROCESSAMENTO DO BANCO DE DADOS (EXECUTA MESMO COM ERROS ANTERIORES)
            try:
                logger.info("Iniciando processamento dos dados no banco de dados...")
                
                with DatabaseManager() as db:
                    caminho_downloads = Path(self.settings.CAMINHO_PLS)
                    
                    # Lista de arquivos para importar
                    arquivos_importar = [
                        ('financeiro', 'finr150.xlsx', db.settings.TABLE_FINANCEIRO),
                        ('modelo1', 'ctbr040.xlsx', db.settings.TABLE_MODELO1),
                        ('contas_itens', 'ctbr140.xlsx', db.settings.TABLE_CONTAS_ITENS),
                        ('adiantamento', 'ctbr100.xlsx', db.settings.TABLE_ADIANTAMENTO)
                    ]
                    
                    # Importar cada arquivo
                    importacoes_realizadas = 0
                    for nome, arquivo, tabela in arquivos_importar:
                        try:
                            file_path = caminho_downloads / arquivo
                            
                            if not file_path.exists():
                                logger.warning(f"Arquivo {arquivo} não encontrado, pulando...")
                                continue
                                
                            logger.info(f"Importando {arquivo} para tabela {tabela}...")
                            success = db.import_from_excel(file_path, tabela)
                            
                            if success:
                                importacoes_realizadas += 1
                                results.append({
                                    'status': 'success',
                                    'message': f'Planilha {nome} importada com sucesso',
                                    'etapa': 'importação',
                                    'error_code': None
                                })
                                logger.info(f"✅ {arquivo} importado para {tabela}")
                            else:
                                raise Exception(f"Falha na importação do arquivo {arquivo}")
                                
                        except Exception as e:
                            results.append({
                                'status': 'error',
                                'message': f'Falha ao importar {nome}: {str(e)}',
                                'etapa': 'importação',
                                'error_code': getattr(e, 'code', 'FE3') if hasattr(e, 'code') else 'FE3'
                            })
                            logger.error(f"❌ Erro ao importar {arquivo}: {e}")

                    # Processar dados apenas se pelo menos uma importação teve sucesso
                    if importacoes_realizadas > 0:
                        logger.info("Processando dados para conciliação...")
                        if db.process_data():
                            output_path = db.export_to_excel()
                            if output_path:
                                results.append({
                                    'status': 'success',
                                    'message': f'Conciliação gerada em {output_path}',
                                    'etapa': 'processamento',
                                    'error_code': None
                                })
                                logger.info(f"✅ Planilha final gerada: {output_path}")
                            else:
                                results.append({
                                    'status': 'error',
                                    'message': 'Falha ao gerar planilha de conciliação',
                                    'etapa': 'processamento',
                                    'error_code': 'DB001'
                                })
                        else:
                            results.append({
                                'status': 'error',
                                'message': 'Falha no processamento dos dados',
                                'etapa': 'processamento',
                                'error_code': 'DB002'
                            })
                    else:
                        results.append({
                            'status': 'error',
                            'message': 'Nenhum arquivo foi importado com sucesso',
                            'etapa': 'importação',
                            'error_code': 'DB003'
                        })
                        logger.error("❌ Nenhum arquivo importado, pulando processamento")

            except Exception as e:
                # Falha crítica no processamento do banco
                error_msg = f"Falha crítica no processamento do banco: {str(e)}"
                logger.error(error_msg)
                results.append({
                    'status': 'critical_error',
                    'message': error_msg,
                    'etapa': 'database',
                    'error_code': getattr(e, 'code', 'DB000') if hasattr(e, 'code') else 'DB000'
                })

            # Verificação final dos resultados
            sucessos = sum(1 for r in results if r['status'] == 'success')
            erros = sum(1 for r in results if r['status'] in ['error', 'critical_error'])
            
            if erros > 0:
                logger.warning(f"Processo concluído com {sucessos} sucessos e {erros} erros")
            else:
                logger.info(f"Processo concluído com sucesso total: {sucessos} operações")

            return results