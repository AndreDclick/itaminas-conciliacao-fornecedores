"""
Módulo de utilitários para automação com Playwright.
Contém funções auxiliares para interação com páginas web, manipulação de dados
e carregamento de parâmetros de configuração.
"""

from playwright.sync_api import Page
from config.logger import configure_logger
from .exceptions import (
    ExcecaoNaoMapeadaError,
    FormSubmitFailed
)

from datetime import datetime, date
from pathlib import Path
import time
import os
import calendar
import json

# Configuração do logger para registro de atividades
logger = configure_logger()

class Utils:
    """Classe utilitária com métodos para auxiliar na automação de tarefas web."""
    
    def __init__(self, page: Page):
        """
        Inicializa a classe Utils com uma instância de página do Playwright.
        
        Args:
            page (Page): Instância da página do Playwright
        """
        self.page = page
        self._definir_locators()
    
    def _definir_locators(self):
        """
        Centraliza a definição de todos os locators usados na automação.
        Os locators são armazenados como variáveis de instância para reutilização.
        """
        self.locators = {
            'popup_fechar': self.page.get_by_role("button", name="Fechar"),
            'botao_confirmar': self.page.get_by_role("button", name="Confirmar"), 
            'botao_marcar_filiais': self.page.get_by_role("button", name="Marca Todos - <F4>")
        }
    
    def _fechar_popup_se_existir(self):
        """
        Tenta fechar popups que possam aparecer durante a execução.
        
        Este método verifica se um popup com botão "Fechar" está visível
        e tenta fechá-lo. Se não encontrar o popup, apenas registra um aviso.
        """
        try:
            time.sleep(5)  # Aguarda possível aparecimento do popup
            if self.locators['popup_fechar'].is_visible():
                self.locators['popup_fechar'].click()
                logger.info("Popup fechado")
        except Exception as e:
            logger.warning(f"Erro ao verificar popup: {e}")
    
    def _confirmar_operacao(self):
        """
        Confirma uma operação clicando no botão "Confirmar".
        
        Após a confirmação, verifica se há popups para fechar.
        
        Raises:
            FormSubmitFailed: Se não conseguir confirmar a operação
        """
        try:
            time.sleep(5)  # Aguarda carregamento do botão
            self.locators['botao_confirmar'].click()
            logger.info("Operação confirmada")
            self._fechar_popup_se_existir()  # Fecha possíveis popups pós-confirmação
        except Exception as e:
            error_msg = "Falha na confirmação da operação"
            logger.error(f"{error_msg}: {e}")
            raise FormSubmitFailed(error_msg) from e
    
    def _selecionar_filiais(self):
        """
        Seleciona todas las filiais disponíveis usando o botão "Marca Todos".
        
        Este método é útil para processos que requerem seleção de múltiplas filiais.
        
        Raises:
            FormSubmitFailed: Se não conseguir selecionar as filiais
        """
        try: 
            time.sleep(3)  # Aguarda carregamento do botão
            if self.locators['botao_marcar_filiais'].is_visible():
                self.locators['botao_marcar_filiais'].click()
                time.sleep(1)  # Pequena pausa após seleção
                self.locators['botao_confirmar'].click()  # Confirma a seleção
                logger.info("Filial selecionada")
        except Exception as e:
            error_msg = "Falha na seleção de filiais"
            logger.error(f"{error_msg}: {e}")
            raise FormSubmitFailed(error_msg) from e
    
    def _calcular_datas_contas_itens(self, data_referencia=None):
        """
        Calcula as datas inicial e final para o relatório Contas X Itens
        conforme as regras especificadas.
        
        Args:
            data_referencia (datetime, optional): Data de referência para cálculo.
                Se None, usa a data atual.
        
        Returns:
            tuple: (data_inicial, data_final) no formato DD/MM/YYYY
        """
        if data_referencia is None:
            data_referencia = datetime.now()
        
        dia = data_referencia.day
        mes = data_referencia.month
        ano = data_referencia.year
        
        # Verifica se é o último dia do mês
        ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
        eh_ultimo_dia = dia == ultimo_dia_mes
        
        if eh_ultimo_dia:
            # Regra para último dia do mês
            # Data Inicial: primeiro dia do mês anterior
            if mes == 1:
                data_inicial = datetime(ano - 1, 12, 1)
            else:
                data_inicial = datetime(ano, mes - 1, 1)
            
            # Data Final: último dia do mês anterior
            if mes == 1:
                ultimo_dia_anterior = calendar.monthrange(ano - 1, 12)[1]
                data_final = datetime(ano - 1, 12, ultimo_dia_anterior)
            else:
                ultimo_dia_anterior = calendar.monthrange(ano, mes - 1)[1]
                data_final = datetime(ano, mes - 1, ultimo_dia_anterior)
        
        # elif dia == 20:
        #     # Regra para dia 20
        #     # Data Inicial: primeiro dia do mês atual
        #     data_inicial = datetime(ano, mes, 1)
            
        #     # Data Final: dia 20 do mês atual
        #     data_final = datetime(ano, mes, 20)
        
        # else:
        #     # Para outros dias, use as regras padrão ou defina um comportamento alternativo
        #     # Aqui estou usando o mesmo comportamento do dia 20 como padrão
        #     data_inicial = datetime(ano, mes, 1)
        #     data_final = datetime(ano, mes, min(dia, 20))  # Usa o menor entre o dia atual e 20
        
        # Formata as datas para o padrão DD/MM/YYYY
        data_inicial_str = data_inicial.strftime('%d/%m/%Y')
        data_final_str = data_final.strftime('%d/%m/%Y')
        
        return data_inicial_str, data_final_str
    
    def datas_contas_itens(self):
        """
        Retorna as datas para o relatório Contas X Itens conforme as regras especificadas.
        
        Returns:
            tuple: (data_inicial, data_final) no formato DD/MM/YYYY
        """
        return self._calcular_datas_contas_itens()
    
    def ultimo_dia_mes_anterior(self):
        """
        Retorna o último dia do mês anterior.
        Conforme documentação: 'Até data Contábil: último dia do mês anterior à data atual'
        
        Returns:
            str: Último dia do mês anterior no formato DD/MM/YYYY
        """
        hoje = datetime.now()
        
        # Calcula mês e ano anterior
        if hoje.month == 1:
            mes_anterior = 12
            ano_anterior = hoje.year - 1
        else:
            mes_anterior = hoje.month - 1
            ano_anterior = hoje.year
        
        # Obtém o último dia do mês anterior
        ultimo_dia = calendar.monthrange(ano_anterior, mes_anterior)[1]
        data_ultimo_dia = datetime(ano_anterior, mes_anterior, ultimo_dia)
        
        return data_ultimo_dia.strftime('%d/%m/%Y')
    
    def _resolver_valor(self, valor):
        """
        Resolve valores que contenham placeholders {{}} chamando funções correspondentes.
        
        Este método permite usar placeholders em configurações que serão substituídos
        por valores dinâmicos durante a execução.
        
        Args:
            valor: Valor a ser resolvido (pode ser string com placeholder ou valor estático)
            
        Returns:
            Valor resolvido (pode ser string, tupla ou qualquer tipo retornado pela função)
        """
        # Verifica se o valor é uma string com placeholder
        if isinstance(valor, str) and valor.startswith('{{') and valor.endswith('}}'):
            placeholder = valor[2:-2].strip()
            
            # Verifica se há especificação de parte da tupla (ex: .inicial ou .final)
            if '.' in placeholder:
                nome_metodo, parte = placeholder.split('.', 1)
                parte = parte.strip()
            else:
                nome_metodo = placeholder
                parte = None
            
            # Mapeamento de métodos disponíveis para resolução
            metodos_disponiveis = {
                'primeiro_e_ultimo_dia': self.primeiro_e_ultimo_dia,
                'obter_ultimo_dia_ano_passado': self.obter_ultimo_dia_ano_passado,
                'data_atual': self._get_data_atual,
                'datas_contas_itens': self.datas_contas_itens,
                'data_futura': self.data_futura,
                'ultimo_dia_mes_anterior': self.ultimo_dia_mes_anterior
            }
            
            # Verifica se o método solicitado está disponível
            if nome_metodo in metodos_disponiveis:
                resultado = metodos_disponiveis[nome_metodo]()
                
                # Trata retornos em tupla com especificação de parte
                if isinstance(resultado, tuple) and parte:
                    if parte == 'inicial' and len(resultado) >= 1:
                        return resultado[0]  # Retorna o primeiro elemento da tupla
                    elif parte == 'final' and len(resultado) >= 2:
                        return resultado[1]  # Retorna o segundo elemento da tupla
                    else:
                        return resultado  # Retorna a tupla completa se parte não especificada corretamente
                else:
                    return resultado  # Retorna o valor simples ou tupla completa
            else:
                logger.warning(f"Método '{nome_metodo}' não encontrado para resolução")
                return valor  # Retorna o valor original se não encontrar o método
        else:
            return valor  # Retorna o valor original se não for um placeholder
    
    def _carregar_parametros(self, arquivo_json: str, chave: str):
        """
        Carrega parâmetros de configuração de um arquivo JSON.
        
        Este método lê um arquivo JSON e extrai os parâmetros para uma chave específica,
        resolvendo quaisquer placeholders encontrados nos valores.
        
        Args:
            arquivo_json (str): Nome do arquivo JSON com os parâmetros
            chave (str): Chave específica dentro do JSON a ser carregada
            
        Raises:
            FileNotFoundError: Se o arquivo JSON não for encontrado
            KeyError: Se a chave especificada não existir no JSON
            JSONDecodeError: Se o arquivo JSON estiver mal formatado
        """
        try:
            caminho_arquivo = Path(__file__).parent.parent / 'config' / arquivo_json
            
            with open(caminho_arquivo, 'r', encoding='utf-8') as file:
                dados = json.load(file)
            
            # Verifica se a chave existe no JSON
            if chave not in dados:
                raise KeyError(f"Chave '{chave}' não encontrada no arquivo {arquivo_json}")
            
            # Carrega os parâmetros e resolve placeholders
            self.parametros = {}
            for param, valor in dados[chave].items():
                self.parametros[param] = self._resolver_valor(valor)
            
            logger.info(f"Parâmetros carregados para chave '{chave}'")
            
        except FileNotFoundError as e:
            logger.error(f"Arquivo {arquivo_json} não encontrado: {e}")
            raise
        except KeyError as e:
            logger.error(f"Erro ao acessar chave no JSON: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            raise
        except Exception as e:
            error_msg = f"Erro inesperado ao carregar parâmetros: {e}"
            logger.error(error_msg)
            raise ExcecaoNaoMapeadaError(error_msg) from e
    
    def _get_data_atual(self):
        """
        Retorna a data atual no formato DD/MM/YYYY.
        
        Returns:
            str: Data atual formatada
        """
        return date.today().strftime('%d/%m/%Y')
    
    def primeiro_e_ultimo_dia(self):
        """
        Retorna uma tupla com o primeiro e último dia do mês atual.
        
        Returns:
            tuple: (primeiro_dia, ultimo_dia) no formato DD/MM/YYYY
        """
        hoje = date.today()
        primeiro_dia = date(hoje.year, hoje.month, 1)
        ultimo_dia = date(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])
        
        return (
            primeiro_dia.strftime('%d/%m/%Y'),
            ultimo_dia.strftime('%d/%m/%Y')
        )
    
    def obter_ultimo_dia_ano_passado(self):
        """
        Retorna o último dia do ano anterior.
        
        Returns:
            str: Último dia do ano anterior no formato DD/MM/YYYY
        """
        ano_passado = date.today().year - 1
        ultimo_dia = date(ano_passado, 12, 31)
        return ultimo_dia.strftime('%d/%m/%Y')
    
    def data_futura(self):
        """
        Define uma data contábil futura para uso em filtros e relatórios.
        
        Returns:
            str: Data contábil futura no formato DD/MM/YYYY
        """
        hoje = datetime.today()
        ano_futuro = hoje.year + 25
        return f"31/12/{ano_futuro}"
    
    def _validar_parametros(self, parametros_obrigatorios: list):
        """
        Valida se todos os parâmetros obrigatórios foram carregados corretamente.
        
        Args:
            parametros_obrigatorios (list): Lista de nomes de parâmetros obrigatórios
            
        Raises:
            ValueError: Se algum parâmetro obrigatório estiver faltando
        """
        for param in parametros_obrigatorios:
            if param not in self.parametros:
                raise ValueError(f"Parâmetro obrigatório '{param}' não encontrado")
        
        logger.info("Todos os parâmetros obrigatórios validados com sucesso")