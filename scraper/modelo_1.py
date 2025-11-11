"""
Módulo para automação do relatório Modelo 1.
Este módulo utiliza Playwright para navegar no sistema, preencher parâmetros
e gerar planilhas do relatório Modelo 1 (Balancete).
"""

from playwright.sync_api import sync_playwright, TimeoutError 
from config.logger import configure_logger
from config.settings import Settings
from .exceptions import (
    Exceptions,
    ExtracaoRelatorioError,
    TimeoutOperacional,
    DownloadFailed,
    ExcecaoNaoMapeadaError
)
from .utils import Utils
from datetime import date
from pathlib import Path
import time

# Configuração do logger para registro de atividades
logger = configure_logger()

class Modelo_1(Utils):
    """Classe para automação do relatório Modelo 1 (Balancete)."""
    
    def __init__(self, page):  
        """
        Inicializa a classe Modelo 1.
        
        Args:
            page: Instância da página do Playwright
        """
        self.page = page
        self.settings = Settings() 
        self.parametros_json = 'Modelo_1'
        self._definir_locators()
        logger.info("Modelo_1 inicializado")

    def _definir_locators(self):
        """Define todos os locators específicos do relatório Modelo 1."""
        self.locators = {
            # Elementos do menu de navegação
            'menu_relatorios': self.page.get_by_text("Relatorios (9)"),
            'submenu_balancetes': self.page.get_by_text("Balancetes (34)"),
            'opcao_modelo1': self.page.get_by_text("Modelo 1", exact=True),
            'popup_fechar': self.page.get_by_role("button", name="Fechar"),
            'botao_confirmar': self.page.get_by_role("button", name="Confirmar"),
            'botao_marcar_filiais': self.page.get_by_role("button", name="Marca Todos - <F4>"),

            # Campos de parâmetros do relatório
            'data_inicial': self.page.locator("#COMP4512").get_by_role("textbox"),
            'data_final': self.page.locator("#COMP4514").get_by_role("textbox"),
            'conta_inicial': self.page.locator("#COMP4516").get_by_role("textbox"),
            'conta_final': self.page.locator("#COMP4518").get_by_role("textbox"),
            'data_lucros_perdas': self.page.locator("#COMP4556").get_by_role("textbox"),
            'grupos_receitas_despesas': self.page.locator("#COMP4562").get_by_role("textbox"),
            'data_sid_art': self.page.locator("#COMP4564").get_by_role("textbox"),
            'num_linha_balancete': self.page.locator("#COMP4566").get_by_role("textbox"),
            'desc_moeda': self.page.locator("#COMP4568").get_by_role("textbox"),
            'selec_filiais': self.page.locator("#COMP4570").get_by_role("combobox"),
            'botao_ok': self.page.locator('button:has-text("Ok")'),

            # Elementos para geração da planilha
            'aba_planilha': self.page.get_by_role("button", name="Planilha"),
            'formato': self.page.locator("#COMP4547").get_by_role("combobox"),
            'botao_imprimir': self.page.get_by_role("button", name="Imprimir"),
            'botao_sim': self.page.get_by_role("button", name="Sim")
        }
        logger.info("Seletores definidos")

    def _navegar_menu(self):
        """
        Navega pelo menu do sistema até a opção Modelo 1.
        
        Raises:
            ExtracaoRelatorioError: Se falhar na navegação do menu
        """
        try:
            logger.info("Iniciando navegação no menu...")
            
            # Espera o menu principal estar disponível
            self.locators['menu_relatorios'].wait_for(state="visible", timeout=10000)
            self.locators['menu_relatorios'].click()
            logger.info("Menu Relatórios clicado")
            
            time.sleep(5)  
            
            # Verifica se o submenu está visível, caso contrário clica novamente
            if not self.locators['submenu_balancetes'].is_visible():
                self.locators['menu_relatorios'].click()
                time.sleep(1)
            
            # Acessa o submenu de balancetes
            self.locators['submenu_balancetes'].click()
            logger.info("Submenu Balancetes clicado")
            time.sleep(1)
            
            # Seleciona a opção Modelo 1
            self.locators['opcao_modelo1'].wait_for(state="visible")
            self.locators['opcao_modelo1'].click()
            logger.info("Modelo 1 selecionada")
            
        except TimeoutError as e:
            error_msg = "Timeout na navegação do menu Modelo 1"
            logger.error(f"{error_msg}: {e}")
            raise TimeoutOperacional(error_msg, "navegação_menu", 12000) from e
        except Exception as e:
            error_msg = "Falha na navegação do menu Modelo 1"
            logger.error(f"{error_msg}: {e}")
            raise ExtracaoRelatorioError(error_msg, "Modelo_1") from e

    def _preencher_parametros(self):
        """
        Preenche todos os parâmetros do relatório Modelo 1.
        
        Raises:
            ExtracaoRelatorioError: Se falhar no preenchimento dos parâmetros
        """
        try:
            logger.info(f"Usando chave JSON: {self.parametros_json}")
            
            input_data_inicial = self.parametros.get('data_inicial')
            input_data_final = self.parametros.get('data_final')
            
            # Obtém outros parâmetros do JSON
            input_conta_inicial = self.parametros.get('conta_inicial')
            input_conta_final = self.parametros.get('conta_final')
            input_data_lucros_perdas = self.parametros.get('data_lucros_perdas')
            input_grupos_receitas_despesas = self.parametros.get('grupos_receitas_despesas')
            input_data_sid_art = self.parametros.get('data_sid_art')
            input_num_linha_balancete = self.parametros.get('num_linha_balancete')
            input_desc_moeda = self.parametros.get('desc_moeda')

            # Preenche campos de data
            self.locators['data_inicial'].wait_for(state="visible")
            self.locators['data_inicial'].click()
            self.locators['data_inicial'].fill(input_data_inicial)
            time.sleep(0.5) 
            
            self.locators['data_final'].click()
            self.locators['data_final'].fill(input_data_final)
            time.sleep(0.5) 
            
            # Preenche campos de conta
            self.locators['conta_inicial'].click()
            self.locators['conta_inicial'].fill(input_conta_inicial)
            time.sleep(0.5) 
            
            self.locators['conta_final'].click()
            self.locators['conta_final'].fill(input_conta_final)
            time.sleep(0.5) 
            
            # Preenche campos específicos do relatório
            self.locators['data_lucros_perdas'].click()
            self.locators['data_lucros_perdas'].fill(input_data_lucros_perdas)
            time.sleep(0.5) 
            
            self.locators['grupos_receitas_despesas'].click()
            self.locators['grupos_receitas_despesas'].fill(input_grupos_receitas_despesas)
            time.sleep(0.5) 
            
            self.locators['data_sid_art'].click()
            self.locators['data_sid_art'].fill(input_data_sid_art)
            time.sleep(0.5) 
            
            self.locators['num_linha_balancete'].click()
            self.locators['num_linha_balancete'].fill(input_num_linha_balancete)
            time.sleep(0.5) 
            
            self.locators['desc_moeda'].click()
            self.locators['desc_moeda'].fill(input_desc_moeda)
            time.sleep(0.5)
            
            # Configura seleção de filiais
            self.locators['selec_filiais'].click()
            time.sleep(0.5)
            self.locators['selec_filiais'].select_option("0")
            time.sleep(0.5)
            
            # Finaliza o preenchimento
            self.locators['botao_ok'].click()
            
        except Exception as e:
            error_msg = "Falha no preenchimento de parâmetros do Modelo 1"
            logger.error(f"{error_msg}: {e}")
            raise ExtracaoRelatorioError(error_msg, "Modelo_1") from e

    def _gerar_planilha(self):
        """
        Gera e baixa a planilha do relatório Modelo 1.
        
        Raises:
            DownloadFailed: Se falhar na geração da planilha
        """
        try: 
            # Acessa a aba de planilha
            self.locators['aba_planilha'].wait_for(timeout=360000)
            time.sleep(1) 
            self.locators['aba_planilha'].click()
            time.sleep(1) 
            
            # Verifica se o formulário está visível
            if not self.locators['formato'].is_visible():
                self.locators['aba_planilha'].click()
                time.sleep(1)
            
            # Seleciona o formato da planilha
            self.locators['formato'].select_option("3")
            time.sleep(1) 
            
            # Espera pelo download com timeout aumentado
            with self.page.expect_download(timeout=360000) as download_info:
                self.locators['botao_imprimir'].click()
                time.sleep(2)
                self._fechar_popup_se_existir()
                if 'botao_sim' in self.locators and self.locators['botao_sim'].is_visible():
                    self.locators['botao_sim'].click()
                
            # Processa o download
            download = download_info.value
            logger.info(f"Download iniciado: {download.suggested_filename}") 
            
            # Aguarda conclusão do download
            download_path = download.path()
            if download_path:
                settings = Settings()
                destino = Path(settings.CAMINHO_PLS) / settings.PLS_MODELO_1
                
                # Garante que o diretório existe
                destino.parent.mkdir(parents=True, exist_ok=True)
                
                # Salva o arquivo
                download.save_as(destino)
                logger.info(f"Arquivo Modelo 1 salvo em: {destino}")
            else:
                error_msg = "Download falhou - caminho não disponível"
                logger.error(error_msg)
                raise DownloadFailed(error_msg)
            
            # Verifica se há botão de confirmação adicional
            if 'botao_sim' in self.locators and self.locators['botao_sim'].is_visible():
                self.locators['botao_sim'].click()
                
        except TimeoutError as e:
            error_msg = "Timeout na geração da planilha Modelo 1"
            logger.error(f"{error_msg}: {e}")
            raise TimeoutOperacional(error_msg, "geracao_planilha", 120000) from e
        except Exception as e:
            error_msg = "Falha na geração da planilha Modelo 1"
            logger.error(f"{error_msg}: {e}")
            raise DownloadFailed(error_msg) from e

    def execucao(self):
        """
        Fluxo principal de execução do relatório Modelo 1.
        
        Returns:
            dict: Resultado da execução com status e mensagem
        """
        try:
            logger.info('Iniciando execução do Modelo 1')
            
            # Carregar os parâmetros do JSON usando o caminho correto do settings
            parameters_path = self.settings.PARAMETERS_DIR 
            self._carregar_parametros(parameters_path, self.parametros_json)

            # Executa o fluxo completo
            self._navegar_menu()
            time.sleep(1) 
            self._confirmar_operacao()
            time.sleep(1) 
            self._fechar_popup_se_existir()
            self._preencher_parametros()
            self._selecionar_filiais()
            self._gerar_planilha()
            
            logger.info(" Modelo 1 executado com sucesso")
            return {
                'status': 'success',
                'message': 'Modelo 1 completo'
            }
            
        except Exception as e:
            error_msg = f"Falha na execução do relatório Modelo 1"
            logger.error(f"{error_msg}: {str(e)}")
            return {
                'status': 'error', 
                'message': error_msg,
                'error_code': getattr(e, 'code', 'FE3') if isinstance(e, Exceptions) else 'FE3'
            }