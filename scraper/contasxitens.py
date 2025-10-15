"""
Módulo para automação do relatório Contas X Itens.
Este módulo utiliza Playwright para navegar no sistema, preencher parâmetros
e gerar planilhas do relatório Contas X Itens.
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
import calendar
import time

# Configuração do logger para registro de atividades
logger = configure_logger()

class Contas_x_itens(Utils):
    """Classe para automação do relatório Contas X Itens."""
    
    def __init__(self, page):  
        """
        Inicializa a classe Contas X Itens.
        
        Args:
            page: Instância da página do Playwright
        """
        self.page = page
        self._definir_locators()
        self.settings = Settings() 
        self.parametros_json = 'Contas_X_Itens'
        logger.info("Contas_x_itens inicializado")

    def _definir_locators(self):
        """Define todos os locators específicos do relatório Contas X Itens."""
        self.locators = {
            # Elementos do menu de navegação
            'menu_relatorios': self.page.get_by_text("Relatorios (9)"),
            'submenu_balancetes': self.page.get_by_text("Balancetes (34)"),
            'opcao_contas_x_itens': self.page.get_by_text("Contas X Itens", exact=True),
            'popup_fechar': self.page.get_by_role("button", name="Fechar"),
            'botao_confirmar': self.page.get_by_role("button", name="Confirmar"),
            'botao_marcar_filiais': self.page.get_by_role("button", name="Marca Todos - <F4>"),

            # Campos de parâmetros do relatório
            'data_inicial': self.page.locator("#COMP4512").get_by_role("textbox"),
            'data_final': self.page.locator("#COMP4514").get_by_role("textbox"),
            'conta_inicial': self.page.locator("#COMP4516").get_by_role("textbox"),
            'conta_final': self.page.locator("#COMP4518").get_by_role("textbox"),
            'contabil_inicial': self.page.locator("#COMP4520").get_by_role("textbox"),
            'contabil_final': self.page.locator("#COMP4522").get_by_role("textbox"),
            'imprime_item': self.page.locator("#COMP4524").get_by_role("combobox"),
            'saldos_zerados': self.page.locator("#COMP4528").get_by_role("combobox"),
            'moeda': self.page.locator("#COMP4530").get_by_role("textbox"),
            'folha_inicial': self.page.locator("#COMP4532").get_by_role("textbox"),
            'imprime_saldos': self.page.locator("#COMP4534").get_by_role("textbox"),
            'imprime_coluna': self.page.locator("#COMP4546").get_by_role("combobox"),
            'imp_tot_cta': self.page.locator("#COMP4548").get_by_role("combobox"),
            'pula_pagina': self.page.locator("#COMP4550").get_by_role("combobox"),
            'salta_linha': self.page.locator("#COMP4552").get_by_role("combobox"),
            'imprime_valor': self.page.locator("#COMP4554").get_by_role("combobox"),
            'impri_cod_item': self.page.locator("#COMP4556").get_by_role("combobox"),
            'divide_por': self.page.locator("#COMP4558").get_by_role("combobox"),
            'impri_cod_conta': self.page.locator("#COMP4560").get_by_role("combobox"),
            'posicao_ant_lp': self.page.locator("#COMP4562").get_by_role("combobox"),
            'data_lucros': self.page.locator("#COMP4564").get_by_role("textbox"),
            'selec_filiais': self.page.locator("#COMP4566").get_by_role("combobox"),
            'botao_ok': self.page.get_by_role("button", name="OK"),
            
            # Elementos para geração da planilha
            'aba_planilha': self.page.get_by_role("button", name="Planilha"),
            'formato': self.page.locator("#COMP4547").get_by_role("combobox"),
            'botao_imprimir': self.page.get_by_role("button", name="Imprimir"),
            'botao_sim': self.page.get_by_role("button", name="Sim")
        }
        logger.info("Seletores definidos")

    def _navegar_menu(self):
        """
        Navega pelo menu do sistema até a opção Contas X Itens.
        
        Raises:
            ExtracaoRelatorioError: Se falhar na navegação do menu
        """
        try:
            logger.info("Iniciando navegação no menu...")
            
            # Espera o menu principal estar disponível
            self.locators['menu_relatorios'].wait_for(state="visible", timeout=10000)
            self.locators['menu_relatorios'].click()
            
            time.sleep(5)  
            
            # Verifica se o submenu está visível, caso contrário clica novamente
            if not self.locators['submenu_balancetes'].is_visible():
                self.locators['menu_relatorios'].click()
                time.sleep(1)
            
            self.locators['submenu_balancetes'].click()
            logger.info("Submenu Balancetes clicado")
            time.sleep(1)
            
            if not self.locators['opcao_contas_x_itens'].is_visible():
                self.locators['submenu_balancetes'].click()
                time.sleep(1)
            # Seleciona a opção Contas X Itens
            self.locators['opcao_contas_x_itens'].wait_for(state="visible")
            self.locators['opcao_contas_x_itens'].click()
            logger.info("Contas x Itens selecionada")
            
        except TimeoutError as e:
            error_msg = "Timeout na navegação do menu Contas X Itens"
            logger.error(f"{error_msg}: {e}")
            raise TimeoutOperacional(error_msg, "navegação_menu", 10000) from e
        except Exception as e:
            error_msg = "Falha na navegação do menu Contas X Itens"
            logger.error(f"{error_msg}: {e}")
            raise ExtracaoRelatorioError(error_msg, "Contas_X_Itens") from e

    def _preencher_parametros(self, conta):
        """
        Preenche todos os parâmetros do relatório Contas X Itens.
        
        Args:
            conta (str): Número da conta a ser processada
            
        Raises:
            ExtracaoRelatorioError: Se falhar no preenchimento dos parâmetros
        """
        logger.info(f"Usando chave JSON: {self.parametros_json}")
        
        input_data_inicial = self.parametros.get('data_inicial')
        input_data_final = self.parametros.get('data_final')
        input_folha_inicial = self.parametros.get('folha_inicial')
        input_desc_moeda = self.parametros.get('desc_moeda')
        input_imprime_saldo = self.parametros.get('imprime_saldo')
        input_data_lucros = self.parametros.get('data_lucros')
        input_contabil_inicial = self.parametros.get('contabil_inicial')
        input_contabil_final = self.parametros.get('contabil_final')
        try:
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
            self.locators['conta_inicial'].fill(conta)
            time.sleep(0.5) 
            
            self.locators['conta_final'].click()
            self.locators['conta_final'].fill(conta)  
            time.sleep(0.5) 

            # Preenche campos de contabil
            self.locators['contabil_inicial'].click()
            self.locators['contabil_inicial'].fill(input_contabil_inicial)
            time.sleep(0.5) 
            
            self.locators['contabil_final'].click()
            self.locators['contabil_final'].fill(input_contabil_final)  
            time.sleep(0.5) 
            
            
            # Configura opções de combobox
            self.locators['imprime_item'].click()     
            self.locators['imprime_item'].select_option("1")
            time.sleep(0.5) 
            
            self.locators['saldos_zerados'].click()  
            self.locators['saldos_zerados'].select_option("1")
            time.sleep(0.5)
            
            # Preenche campos de texto
            self.locators['moeda'].click()
            self.locators['moeda'].fill(input_desc_moeda)
            time.sleep(0.5) 
            
            self.locators['folha_inicial'].click()
            self.locators['folha_inicial'].fill(input_folha_inicial)
            time.sleep(0.5) 
            
            self.locators['imprime_saldos'].click()
            self.locators['imprime_saldos'].fill(input_imprime_saldo)
            time.sleep(0.5) 
            
            # Continua preenchendo as demais opções
            self.locators['imprime_coluna'].click()
            self.locators['imprime_coluna'].select_option("0")
            time.sleep(0.5)
            
            self.locators['imp_tot_cta'].click()
            self.locators['imp_tot_cta'].select_option("0")
            time.sleep(0.5)
            
            self.locators['pula_pagina'].click()
            self.locators['pula_pagina'].select_option("0")
            
            self.locators['salta_linha'].click()
            self.locators['salta_linha'].select_option("1")
            time.sleep(0.5)
            
            self.locators['imprime_valor'].click()
            self.locators['imprime_valor'].select_option("1")
            time.sleep(0.5)
            
            self.locators['impri_cod_item'].click()
            self.locators['impri_cod_item'].select_option("0")
            time.sleep(0.5)
            
            self.locators['divide_por'].click()
            self.locators['divide_por'].select_option("0")
            time.sleep(0.5)
            
            self.locators['impri_cod_conta'].click()
            self.locators['impri_cod_conta'].select_option("0")
            time.sleep(0.5)
            
            self.locators['posicao_ant_lp'].click()
            self.locators['posicao_ant_lp'].select_option("1")
            time.sleep(0.5)
            
            self.locators['data_lucros'].click()
            self.locators['data_lucros'].fill(input_data_lucros)
            time.sleep(0.5)
            
            self.locators['selec_filiais'].click()
            self.locators['selec_filiais'].select_option("0")
            time.sleep(0.5)
            
            # Finaliza o preenchimento
            self.locators['botao_ok'].click()
            
        except Exception as e:
            error_msg = f"Falha no preenchimento de parâmetros para conta {conta}"
            logger.error(f"{error_msg}: {e}")
            raise ExtracaoRelatorioError(error_msg, "Contas_X_Itens") from e

    def _gerar_planilha(self, conta):
        """
        Gera e baixa a planilha do relatório.
        
        Args:
            conta (str): Número da conta sendo processada
            
        Raises:
            DownloadFailed: Se falhar na geração da planilha
        """
        try: 
            self.locators['aba_planilha'].wait_for(timeout=360000)
            time.sleep(1) 
            self.locators['aba_planilha'].click()
            time.sleep(1) 
            
            if not self.locators['formato'].is_visible():
                self.locators['aba_planilha'].click()
                time.sleep(1)
            # self.locators['formato'].select_option("2")
            self.locators['formato'].select_option("3")

            # Esperar pelo download com timeout aumentado
            with self.page.expect_download(timeout=360000) as download_info:
                self.locators['botao_imprimir'].click()
                logger.info(f"Botão download clicado")
                time.sleep(2)
                if 'botao_imprimir' in self.locators and self.locators['botao_imprimir'].is_visible():
                    self.locators['botao_imprimir'].click()
                    time.sleep(2)
                if 'botao_sim' in self.locators and self.locators['botao_sim'].is_visible():
                    self.locators['botao_sim'].click()
                    logger.info(f"Botão sim clicado")
                time.sleep(2)
                self._fechar_popup_se_existir()
                
            
            download = download_info.value
            logger.info(f"Download iniciado: {download.suggested_filename}") 
            
            # Aguardar conclusão do download
            download_path = download.path()
            if download_path:
                settings = Settings()
                if conta == "10106020001":
                    # destino = Path(settings.CAMINHO_PLS) / "ctbr100.xml"
                    destino = Path(settings.CAMINHO_PLS) / "ctbr100.xlsx"
                else:
                    # destino = Path(settings.CAMINHO_PLS) / "ctbr140.xml"
                    destino = Path(settings.CAMINHO_PLS) / "ctbr140.xlsx"
                                
                
                destino.parent.mkdir(parents=True, exist_ok=True)
                
                download.save_as(destino)
                logger.info(f"Arquivo Contas x itens salvo em: {destino}")
            else:
                logger.error("Download falhou - caminho não disponível")
            
            
        except TimeoutError as e:
            error_msg = f"Timeout na geração da planilha para conta {conta}"
            logger.error(f"{error_msg}: {e}")
            raise TimeoutOperacional(error_msg, "geracao_planilha", 210000) from e
        except Exception as e:
            error_msg = f"Falha na geração da planilha para conta {conta}"
            logger.error(f"{error_msg}: {e}")
            raise DownloadFailed(error_msg) from e

    def _processar_conta(self, conta):
        """
        Processa uma conta individual completa.
        
        Args:
            conta (str): Número da conta a ser processada
            
        Raises:
            ExtracaoRelatorioError: Se falhar no processamento da conta
        """
        try:
            logger.info(f'Processando conta: {conta}')
            
            self._navegar_menu()
            time.sleep(1) 
            self._confirmar_operacao()  
            time.sleep(1) 
            self._fechar_popup_se_existir()  
            time.sleep(1) 
            self._fechar_popup_se_existir()  
            self._preencher_parametros(conta)  
            self._selecionar_filiais()  
            self._gerar_planilha(conta)
            logger.info(f"✅ Conta {conta} processada com sucesso")
            
        except Exception as e:
            error_msg = f"Falha no processamento da conta {conta}"
            logger.error(f"{error_msg}: {str(e)}")
            raise ExtracaoRelatorioError(error_msg, "Contas_X_Itens") from e

    def execucao(self):
        """
        Fluxo principal de execução para todas as contas.
        
        Returns:
            dict: Resultado da execução com status e mensagem
        """
        try:

            contas = ["10106020001", "20102010001"]
            # Carregar os parâmetros do JSON usando o caminho correto do settings
            parameters_path = self.settings.PARAMETERS_DIR 
            self._carregar_parametros(parameters_path, self.parametros_json)

            for conta in contas:
                self._processar_conta(conta)
                
            return {
                'status': 'success',
                'message': f'Todas as {len(contas)} contas processadas com sucesso'
            }
            
                
        except Exception as e:
            error_msg = f"Falha na execução do relatório Contas X Itens"
            logger.error(f"{error_msg}: {str(e)}")
            return {
                'status': 'error', 
                'message': error_msg,
                'error_code': getattr(e, 'code', 'FE3') if isinstance(e, Exceptions) else 'FE3'
            }