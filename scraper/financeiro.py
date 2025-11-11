"""
Arquivo financeiro.py

Automação de extração de dados financeiros do sistema Protheus, executando a navegação,  o preenchimento dos parâmetros, o download de planilhas e  o tratamento de exceções específicas do processo.
Este módulo foi estruturado para tornar mais clara a manutenção e o entendimento do fluxo de extração, permitindo a sustentação de forma ágil e segura.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from config.logger import configure_logger
from config.settings import Settings
from .utils import Utils
from .exceptions import DownloadFailed, TimeoutOperacional
from datetime import datetime, timedelta
from pathlib import Path


import calendar
import time
import os
from pathlib import Path

logger = configure_logger()

# Automação e extração dos dados financeiros no sistema protheus (navegação e download).
class ExtracaoFinanceiro(Utils):
    # Inicialização e seleção dos seletores da interface, para carregas as configurações.
    def __init__(self, page):
        self.page = page
        self._definir_locators()
        self.settings = Settings()
        self.parametros_json = 'Financeiro' 
        logger.info("Financeiro inicializada")

    # armazenamento dos seletores utilizados na automação para facilitar caso haja mudanças.
    def _definir_locators(self):
        """Centraliza os locators específicos da extração financeira"""
        self.locators = {
            # Navegação
            'menu_relatorios': self.page.get_by_text("Relatorios (9)"),
            # 'menu_financeiro': self.page.get_by_text("Financeiro (2)"),
            'menu_financeiro': self.page.get_by_text("Financeiro (5)"),
            'menu_titulos_a_pagar': self.page.get_by_text("Títulos a Pagar", exact=True),
            'popup_fechar': self.page.get_by_role("button", name="Fechar"),
            'botao_confirmar': self.page.get_by_role("button", name="Confirmar"),
            'botao_marcar_filiais': self.page.get_by_role("button", name="Marca Todos - <F4>"),
            'confirmar_moeda': self.page.get_by_text("Moedas"),

            # Janela "Posição dos Títulos a Pagar"
            'planilha': self.page.get_by_role("button", name="Planilha"),
            'tipo_de_planilha': self.page.locator('#COMP4547').get_by_role('combobox'),
            'outras_acoes': self.page.get_by_role('button', name='Outras Ações'),
            'parametros_menu': self.page.get_by_text('Parâmetros'),
            'imprimir_btn': self.page.get_by_role('button', name='Imprimir'),
            'botao_sim': self.page.get_by_role("button", name="Sim"),

            # Janela de Parâmetros
            'do_vencimento': self.page.locator('#COMP6024').get_by_role('textbox'),
            'ate_o_vencimento': self.page.locator('#COMP6026').get_by_role('textbox'),
            'da_emissao': self.page.locator('#COMP6036').get_by_role('textbox'),
            'ate_a_emissao': self.page.locator('#COMP6038').get_by_role('textbox'),
            'da_data_contabil': self.page.locator('#COMP6046').get_by_role('textbox'),
            'ate_a_data_contabil': self.page.locator('#COMP6048').get_by_role('textbox'),
            'data_base': self.page.locator('#COMP6076').get_by_role('textbox'),
            'ok_btn': self.page.get_by_role('button', name='OK'),
            
            # Janela de Seleção de Filiais
            'selecao_filiais_janela': self.page.get_by_text('Seleção de filiais'),
            'matriz_filial_checkbox': self.page.get_by_text('Matriz e Filial'), # Se houver checkbox para isso
            'marcar_todos_btn': self.page.get_by_role('button', name='Marca Todos - <F4>'),
            'confirmar': self.page.get_by_role('button', name='Confirmar'),

            #Janela confirmar filiais
            'nao': self.page.get_by_role('button', name='Não'),
        }
        logger.info("Seletores definidos")

    
    # navegação pela página e tratamento de pop ups e confirmações.
    def _navegar_e_configurar_planilha(self):
        """Navega para a tela de Títulos a Pagar e configura a extração para planilha."""
        try:
            try:
                self.locators['menu_relatorios'].wait_for(state="visible", timeout=10000)
            except PlaywrightTimeoutError:
                logger.error("Timeout ao aguardar menu_relatorios")
                raise TimeoutOperacional("Timeout na operação", operacao="aguardar menu_relatorios", tempo_limite=10)
            self.locators['menu_relatorios'].click()
            logger.info("Iniciando navegação no menu...")
            time.sleep(2)  
            if not self.locators['menu_financeiro'].is_visible():
                self.locators['menu_relatorios'].click()
                time.sleep(1)
            self.locators['menu_financeiro'].click()
            time.sleep(1)
            try:
                self.locators['menu_titulos_a_pagar'].wait_for(state="visible", timeout=10000)
            except PlaywrightTimeoutError:
                logger.error("Timeout ao aguardar menu_titulos_a_pagar")
                # Exception TimeoutOperacional
                raise TimeoutOperacional("Timeout na operação", operacao="aguardar menu_titulos_a_pagar", tempo_limite=10)
            self.locators['menu_titulos_a_pagar'].click()    
            self._confirmar_operacao()
            time.sleep(2)
            self._fechar_popup_se_existir()
            time.sleep(1)
            if self.locators['popup_fechar'].is_visible():
                self.locators['popup_fechar'].click()
        # Exception TimeoutOperacional
        except TimeoutOperacional as e:
            logger.error(f"Timeout operacional: {e}")
            raise
        except Exception as e:
            logger.error("Falha na navegação ou configuração da planilha")
            raise

    
    def _confirmar_moeda(self):
        time.sleep(3)
        if self.locators['confirmar_moeda'].is_visible():
                self.locators['botao_confirmar'].click()

    # navegação para escolha do tipo de planilha que deve ser criada.
    def _criar_planilha (self):
        try:
            try:
                self.locators['planilha'].wait_for(state="visible", timeout=120000)
            except PlaywrightTimeoutError:
                logger.error("Timeout ao aguardar botão de planilha")
                raise TimeoutOperacional("Timeout na operação", operacao="aguardar botão de planilha", tempo_limite=10)
            time.sleep(1)
            self.locators['planilha'].click()
            time.sleep(1)
            if not self.locators['tipo_de_planilha'].is_visible():
                self.locators['planilha'].click()
                time.sleep(1)
            self.locators['tipo_de_planilha'].select_option("3")
            time.sleep(1)
        # Exception TimeoutOperacional    
        except TimeoutOperacional as e:
            logger.error(f"Timeout operacional: {e}")
            raise
        except Exception as e:
            logger.error(f"Falha na escolha impressão de planilha {e}")
            raise

    # Define a data de fechamento do mês anterior (considerando dia útil)
    def _outras_acoes(self):
        """Método para lidar com outras ações."""
        try:
            logger.info("Acessando outras ações")
            # Na opção "Outras Ações", selecionar "Parâmetros" 
            self.locators['outras_acoes'].click()
            self.locators['parametros_menu'].click()
            self.locators['imprimir_btn'].click()
            time.sleep(5)
        except Exception as e:
            logger.error(f"Falha ao acessar outras ações: {e}")
            raise

    def fechamento_mes(self):
        hoje = datetime.today()
        mes_passado = hoje.month - 1 if hoje.month > 1 else 12
        ano_mes_passado = hoje.year if hoje.month > 1 else hoje.year - 1
        ultimo_dia = calendar.monthrange(ano_mes_passado, mes_passado)[1]
        data_formatada = datetime(ano_mes_passado, mes_passado, ultimo_dia).strftime("%d/%m/%Y")
        return data_formatada

    # Carrega os parâmetros definidos no JSON (parameters.json)
    def _preencher_parametros(self):
        try:
            logger.info(f"Usando chave JSON: {self.parametros_json}")

            # Valores carregados do JSON
            input_do_vencimento = self.parametros.get('do_vencimento')
            input_ate_o_vencimento = self.parametros.get('ate_o_vencimento')
            input_da_emissao = self.parametros.get('da_emissao')
            input_ate_a_emissao = self.parametros.get('ate_a_emissao')
            input_da_data_contabil = self.parametros.get('da_data_contabil')
            input_ate_a_data_contabil = self.parametros.get('ate_a_data_contabil')
            input_data_base = self.parametros.get('data_base')

            # parâmetros
            self.locators['do_vencimento'].wait_for(state="visible")
            self.locators['do_vencimento'].click()
            self.locators['do_vencimento'].fill(input_do_vencimento)
            time.sleep(0.5)
            self.locators['ate_o_vencimento'].click()
            self.locators['ate_o_vencimento'].fill(input_ate_o_vencimento)
            time.sleep(0.5)
            self.locators['da_emissao'].click()
            self.locators['da_emissao'].fill(input_da_emissao)
            time.sleep(0.5)
            self.locators['ate_a_emissao'].click()
            self.locators['ate_a_emissao'].fill(input_ate_a_emissao)
            time.sleep(0.5)
            self.locators['da_data_contabil'].click()
            self.locators['da_data_contabil'].fill(input_da_data_contabil)
            time.sleep(0.5)
            self.locators['ate_a_data_contabil'].click()
            self.locators['ate_a_data_contabil'].fill(input_ate_a_data_contabil)
            time.sleep(0.5)
            self.locators['data_base'].click()
            self.locators['data_base'].fill(input_data_base)
            time.sleep(0.5)
            self.locators['ok_btn'].click()
            logger.info("Parâmetros preenchidos com sucesso")

        except Exception as e:
            logger.error(f"Falha no preenchimento de parâmetros {e}")
            raise


    # processo de impressão e download da planilha, salvando-a no local determinado. Tratando possíveis falhas no download.
    def _imprimir_e_baixar(self):
        """Clica no botão de imprimir e baixa o arquivo"""
        try:
            logger.info("Aguardando botão de impressão.")
            self.locators['imprimir_btn'].wait_for(state='visible', timeout=30000)
            time.sleep(2)
            
            # Esperar pelo download
            with self.page.expect_download(timeout=300000) as download_info:
                self.locators['imprimir_btn'].click()
                logger.info(f"botão download clicado")
                time.sleep(2)
                if 'botao_sim' in self.locators and self.locators['botao_sim'].is_visible():
                    self.locators['botao_sim'].click()
                    time.sleep(2)
                self._fechar_popup_se_existir()
                self._selecionar_filiais()
            self._confirmar_filiais()
            
            download = download_info.value
            logger.info(f"Download iniciado: {download.suggested_filename}")
            
            # Aguardar conclusão do download
            download_path = download.path()
            if download_path:
                settings = Settings()
                destino = Path(settings.CAMINHO_PLS) / settings.PLS_FINANCEIRO
                destino.parent.mkdir(parents=True, exist_ok=True)
                
                # Salvar o arquivo
                download.save_as(destino)
                logger.info(f"Arquivo Financeiro salvo em: {destino}")
            else:
                logger.error("Download falhou - caminho não disponível")
            
            if 'botao_sim' in self.locators and self.locators['botao_sim'].is_visible():
                    self.locators['botao_sim'].click()
            logger.info("Processo de download concluído")

        except Exception as e:
            logger.error(f"Falha na impressão/baixar da planilha: {e}")
            raise
    
    # confirmação das filiais a serem incluídas na planilha, tratando pop-ups e confirmações.
    def _confirmar_filiais(self):
        try:
            time.sleep(2) 
            if self.locators['nao'].is_visible():
                time.sleep(1)             
                self.locators['nao'].click()
                logger.info("Botão 'Não' clicado")
        except Exception as e:
            logger.error(f"Falha ao clicar no botão 'Não': {e}")

    # fluxo principal de execução da extração financeira, iniciando da navegação até o download da planilha.
    def execucao(self):
        """Fluxo principal de extração de planilha financeira."""
        try:
            # Carregar os parâmetros do JSON usando o caminho correto do settings
            parameters_path = self.settings.PARAMETERS_DIR  
            self._carregar_parametros(parameters_path, self.parametros_json)

            self._navegar_e_configurar_planilha()            
            # self._confirmar_moeda()
            self._criar_planilha()
            self._outras_acoes()
            self._preencher_parametros()
            self._imprimir_e_baixar()
            logger.info("Extração da planilha financeira executada com sucesso")
            return {
                'status': 'success',
                'message': 'Financeiro completo'
            }
            
        except Exception as e:
            error_msg = f" Falha na execução: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}