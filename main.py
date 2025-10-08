"""
Sistema de Conciliação de Fornecedores Itaminas
Módulo de envio de emails e configurações do sistema
Desenvolvido por DCLICK
"""

import logging
import os
import psutil
import win32com.client
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from jinja2 import Template

# Importações locais para evitar dependências circulares
from scraper.protheus import ProtheusScraper
from config.logger import configure_logger
from config.settings import Settings
from scraper.exceptions import (
    PlanilhaFormatacaoErradaError,
    LoginProtheusError,
    ExtracaoRelatorioError,
    TimeoutOperacional,
    DiferencaValoresEncontrada,
    DataInvalidaConciliação,
    FornecedorNaoEncontrado
)

#E-mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import time

import traceback
import sys
# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    print("=== ERRO NÃO TRATADO ===")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("========================")

sys.excepthook = handle_exception

def send_email_gmail(host, port, from_addr, password, subject, to_addrs, 
                    html_content, embedded_images=None, attachments=None):
    """
    Função para enviar email via Gmail (implementação real)
    
    Args:
        host (str): Servidor SMTP
        port (int): Porta do servidor SMTP
        from_addr (str): Email remetente
        password (str): Senha do email remetente
        subject (str): Assunto do email
        to_addrs (list): Lista de destinatários
        html_content (str): Conteúdo HTML do email
        embedded_images (list, optional): Lista de imagens para embedar
        attachments (list, optional): Lista de anexos
        
    Returns:
        bool: True se o email foi enviado com sucesso
    """
    try:
        # Criar mensagem
        msg = MIMEMultipart('related')
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = ', '.join(to_addrs)
        
        # Criar alternativa para texto simples (fallback)
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        
        # Criar versão HTML
        msg_html = MIMEText(html_content, 'html', 'utf-8')
        msg_alternative.attach(msg_html)
        
        # Processar imagens embedadas
        # if embedded_images:
        #     for img_path in embedded_images:
        #         try:
        #             img_name = os.path.basename(img_path)
        #             with open(img_path, 'rb') as img_file:
        #                 img_part = MIMEBase('application', 'octet-stream')
        #                 img_part.set_payload(img_file.read())
        #                 encoders.encode_base64(img_part)
        #                 img_part.add_header('Content-Disposition', f'inline; filename="{img_name}"')
        #                 img_part.add_header('Content-ID', f'<{img_name}>')
        #                 msg.attach(img_part)
        #         except Exception as e:
        #             print(f"Erro ao anexar imagem {img_path}: {e}")
        
        # Processar anexos
        if attachments:
            for attachment_path in attachments:
                try:
                    attachment_name = os.path.basename(attachment_path)
                    with open(attachment_path, 'rb') as file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(file.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 
                                    f'attachment; filename="{attachment_name}"')
                        msg.attach(part)
                except Exception as e:
                    print(f"Erro ao anexar arquivo {attachment_path}: {e}")
        
        # Enviar email
        with smtplib.SMTP(host, port) as server:
            server.starttls()  # Upgrade para conexão segura
            server.login(from_addr, password)
            server.send_message(msg)
        
        print(f"Email enviado com sucesso para: {to_addrs}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False


def send_email(subject, body, summary, attachments=None, email_type="success"):
    """
    Envia email seguindo o padrão da empresa para o processo de Conciliação de Fornecedores
    
    Args:
        subject (str): Assunto do email
        body (str): Corpo principal do email (deve conter {1} e {2} para substituição)
        summary (list): Lista com resumo da execução (substituirá {3})
        attachments (list, optional): Lista de caminhos de arquivos para anexar
        email_type (str): Tipo de email ("success" ou "error")
    """
    # Configurações
    settings = Settings()
    
    # Verificar se o envio de email está habilitado
    if not settings.SMTP["enabled"]:
        logging.info("Envio de email desabilitado pela configuração")
        return

    # Definir destinatários com base no tipo de email
    if email_type == "success":
        recipients = settings.EMAILS["success"]
    else:
        recipients = settings.EMAILS["error"]

    # Preparar lista de anexos
    if attachments is None:
        attachments = []
    
    # Adicionar arquivo de log padrão se disponível
    log_path = settings.LOGS_DIR / f"conciliacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    if log_path.exists():
        attachments.append(str(log_path))

    # Construir caminhos absolutos para imagens
    # logo_path = settings.BASE_DIR / settings.SMTP["logo"]
    template_path = settings.BASE_DIR / settings.SMTP["template"]
    
    # Processar o corpo para extrair {1} e {2}
    body_parts = body.split('\n')
    part1 = body_parts[0] if len(body_parts) > 0 else ""
    part2 = body_parts[1] if len(body_parts) > 1 else ""
    
    # Formatar o resumo
    summary_html = "<br/>".join(summary)
    
    # Tentar carregar template HTML
    try:
        with open(template_path, 'r', encoding='utf-8') as template_file:
            template_content = template_file.read()
            
            # Substituir os placeholders manualmente
            html_content = template_content.replace('{0}', subject)
            html_content = html_content.replace('{1}', part1)
            html_content = html_content.replace('{2}', part2)
            html_content = html_content.replace('{3}', summary_html)
            
    except FileNotFoundError:
        # Template HTML simplificado se o arquivo não for encontrado
        html_content = f"""
        <html>
        <body>
            <h2>{subject}</h2>
            <p>{part1}</p>
            <p>{part2}</p>
            <pre>{chr(10).join(summary)}</pre>
            <p>Esta mensagem foi gerada automaticamente pelo sistema de Conciliação de Fornecedores Itaminas.</p>
            <p>Desenvolvido por DCLICK.</p>
        </body>
        </html>
        """
        logging.warning("Template HTML não encontrado, usando template simplificado")
    
    # Registrar tentativa de envio de email
    logging.info("Enviando e-mail...")
    
    # Enviar email usando a função de envio REAL
    success = send_email_gmail(
        settings.SMTP["host"], 
        settings.SMTP["port"], 
        settings.SMTP["from"], 
        settings.SMTP["password"], 
        subject, 
        recipients, 
        html_content,
        # [str(logo_path)], 
        attachments       
    )
    
    if success:
        logging.info("Email enviado com sucesso")
    else:
        logging.error("Falha ao enviar email")

def send_success_email(completion_time, processed_count, error_count, report_path=None):
    """
    Envia email de sucesso conforme especificado na documentação
    
    Args:
        completion_time (str): Data/hora de conclusão do processo
        processed_count (int): Total de registros processados
        error_count (int): Total de exceções identificadas
        report_path (str, optional): Caminho para o relatório final
    """
    # Configurar assunto do email
    subject = "[SUCESSO] BOT - Conciliação de Fornecedores Itaminas"
    
    # Corpo principal do email (com placeholders {1} e {2})
    body = "O processo de conciliação de fornecedores foi realizado com sucesso.\nTodos os detalhes do processamento estão no log em anexo."
    
    # Criar resumo da execução
    summary = [
        f"Status: Concluído com sucesso",
        f"Data/Hora de conclusão: {completion_time}",
        f"Total de registros processados: {processed_count}",
        f"Total de exceções identificadas: {error_count}",
    ]
    
    # Adicionar localização do relatório se disponível
    if report_path:
        summary.append(f"Localização do relatório final: {report_path}")
    
    # Preparar lista de anexos
    attachments = []
    if report_path:
        attachments.append(report_path)
    
    # Configurações
    settings = Settings()
    
    # Adicionar planilhas geradas como anexos
    planilha_financeiro = settings.DATA_DIR / settings.PLS_FINANCEIRO
    planilha_modelo = settings.DATA_DIR / settings.PLS_MODELO_1
    
    if planilha_financeiro.exists():
        attachments.append(str(planilha_financeiro))
    if planilha_modelo.exists():
        attachments.append(str(planilha_modelo))
    
    # Enviar email de sucesso
    send_email(subject, body, summary, attachments, "success")

def send_error_email(error_time, error_description, affected_count=None, 
                    error_records=None, suggested_action=None):
    """
    Envia email de erro conforme especificado na documentação
    
    Args:
        error_time (str): Data/hora da ocorrência do erro
        error_description (str): Descrição do erro
        affected_count (int, optional): Quantidade de registros afetados
        error_records (list, optional): Lista de registros com erro
        suggested_action (str, optional): Ação sugerida para correção
    """
    # Configurar assunto do email
    subject = "[FALHA] BOT - Conciliação de Fornecedores Itaminas"
    
    # Corpo principal do email (com placeholders {1} e {2})
    body = "Falha na execução do processo de conciliação de fornecedores.\nVerifique os logs em anexo para mais detalhes."
    
    # Criar resumo do erro
    summary = [
        f"Status: Falha na execução",
        f"Data/Hora da ocorrência: {error_time}",
        f"Tipo de erro: {error_description}",
    ]
    
    # Adicionar informações sobre registros afetados se disponível
    if affected_count is not None:
        summary.append(f"Quantidade de registros afetados: {affected_count}")
    
    # Adicionar identificação de registros com erro se disponível
    if error_records:
        records_str = ", ".join(str(record) for record in error_records[:10])  # Limitar a 10 registros
        if len(error_records) > 10:
            records_str += f"... (e mais {len(error_records) - 10})"
        summary.append(f"Identificação de registros com erro: {records_str}")
    
    # Adicionar ação sugerida se disponível
    if suggested_action:
        summary.append(f"Ação sugerida para correção: {suggested_action}")
    
    # Enviar email de erro
    send_email(subject, body, summary, None, "error")


def send_error_email(error_time, error_description, affected_count=None, 
                    error_records=None, suggested_action=None):
    """
    Envia email de erro conforme especificado na documentação
    
    Args:
        error_time (str): Data/hora da ocorrência do erro
        error_description (str): Descrição do erro
        affected_count (int, optional): Quantidade de registros afetados
        error_records (list, optional): Lista de registros com erro
        suggested_action (str, optional): Ação sugerida para correção
    """
    # Configurar assunto do email
    subject = "[FALHA] BOT - Conciliação de Fornecedores Itaminas"
    
    # Corpo principal do email
    body = "Falha na execução do processo de conciliação de fornecedores. Verifique os logs em anexo para mais detalhes."
    
    # Criar resumo do erro
    summary = [
        f"Status: Falha na execução",
        f"Data/Hora da ocorrência: {error_time}",
        f"Tipo de erro: {error_description}",
    ]
    
    # Adicionar informações sobre registros afetados se disponível
    if affected_count is not None:
        summary.append(f"Quantidade de registros afetados: {affected_count}")
    
    # Adicionar identificação de registros com erro se disponível
    if error_records:
        records_str = ", ".join(str(record) for record in error_records[:10])  # Limitar a 10 registros
        if len(error_records) > 10:
            records_str += f"... (e mais {len(error_records) - 10})"
        summary.append(f"Identificação de registros com erro: {records_str}")
    
    # Adicionar ação sugerida se disponível
    if suggested_action:
        summary.append(f"Ação sugerida para correção: {suggested_action}")
    
    # Enviar email de erro
    send_email(subject, body, summary, None, "error")


def handle_specific_exceptions(e, logger):
    """
    Trata exceções específicas e retorna informações para o email de erro
    
    Args:
        e: Exceção capturada
        logger: Logger para registro
        
    Returns:
        tuple: (error_description, affected_count, suggested_action)
    """
    error_description = str(e)
    affected_count = None
    suggested_action = "Verificar logs para detalhes completos do erro."
    
    # Mapeamento de exceções específicas
    if isinstance(e, PlanilhaFormatacaoErradaError):
        suggested_action = "Verificar formatação das planilhas extraídas"
        error_description = f"Erro de formatação na planilha: {e.caminho_arquivo}"
        
    elif isinstance(e, LoginProtheusError):
        suggested_action = "Verificar credenciais de acesso ao Protheus"
        error_description = f"Falha no login do usuário: {e.usuario}"
        
    elif isinstance(e, ExtracaoRelatorioError):
        suggested_action = "Verificar conexão com o sistema Protheus"
        error_description = f"Falha na extração do relatório: {e.relatorio}"
        
    elif isinstance(e, TimeoutOperacional):
        suggested_action = "Aumentar tempo de espera para resposta do sistema"
        error_description = f"Timeout na operação: {e.operacao} (limite: {e.tempo_limite}s)"
        
    elif isinstance(e, DiferencaValoresEncontrada):
        suggested_action = "Verificar inconsistências nos valores financeiros e contábeis"
        error_description = f"Diferença de valores para fornecedor {e.fornecedor}"
        
    elif isinstance(e, DataInvalidaConciliação):
        suggested_action = "Verificar data informada para conciliação"
        error_description = f"Data inválida: {e.data_informada}"
        
    elif isinstance(e, FornecedorNaoEncontrado):
        suggested_action = "Verificar código/nome do fornecedor nos sistemas"
        error_description = f"Fornecedor não encontrado: {e.codigo_fornecedor or e.nome_fornecedor}"
    
    # Log da exceção
    logger.error(f"Exceção {type(e).__name__}: {error_description}", exc_info=True)
    
    return error_description, affected_count, suggested_action


def excluir_arquivos_pasta(CAMINHO_PLS):
    """
    Exclui todos os arquivos de uma pasta específica.
    """
    try:
        pasta = Path(CAMINHO_PLS)
        
        arquivos_excluidos = []
        quantidade_excluida = 0
        
        for item in pasta.iterdir():
            if item.is_file():
                try:
                    item.unlink()
                    arquivos_excluidos.append(item.name)
                    quantidade_excluida += 1
                    logging.info(f"Arquivo excluído: {item.name}")  
                except Exception as e:
                    logging.error(f"Erro ao excluir {item.name}: {e}")
        
        logging.info(f"Total de arquivos excluídos: {quantidade_excluida}")
        return quantidade_excluida, arquivos_excluidos
        
    except Exception as e:
        logging.error(f"Erro ao excluir arquivos da pasta {CAMINHO_PLS}: {e}")
        return 0, []
        


def fechar_web_agent():
    logger = configure_logger()
    
    # Fechar o Microsoft Edge
    processo_nome = "msedge.exe"
    
    processos_fechados = 0
    
    for processo in psutil.process_iter(['pid', 'name']):
        if processo.info['name'].lower() == processo_nome.lower():
            try:
                processo.terminate()
                processo.wait(timeout=3)
                logger.info(f"Microsoft Edge fechado (PID: {processo.info['pid']})")
                processos_fechados += 1
            except psutil.NoSuchProcess:
                logger.warning("Processo do Edge já foi fechado")
            except psutil.TimeoutExpired:
                processo.kill()
                logger.info(f"Microsoft Edge forçado a fechar (PID: {processo.info['pid']})")
                processos_fechados += 1
    
    if processos_fechados > 0:
        logger.info(f"Total de processos do Edge fechados: {processos_fechados}")
        return True
    else:
        logger.warning("Microsoft Edge não encontrado em execução")
        return False
    
def get_latest_file(folder: Path, prefix="CONCILIACAO_", extension=".xlsx"):
    """
    Retorna o caminho do arquivo mais recente na pasta `folder`
    que começa com `prefix` e termina com `extension`.
    """
    files = [f for f in folder.glob(f"{prefix}*{extension}") if f.is_file()]
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)
# =============================================================================
# FUNÇÃO PRINCIPAL E EXECUÇÃO DO SCRIPT
# =============================================================================

def main():
    """
    Função principal do script de conciliação de fornecedores
    """
    # Configurar logger
    logger = configure_logger()

    settings=Settings()

    # Execução do web agent
    # os.startfile(settings.WEB_AGENT_PATH)
    # logger.info("Web Agent iniciado")

    # time.sleep(7)


    # Limpar pasta de dados antes de começar
    # quantidade = excluir_arquivos_pasta(settings.CAMINHO_PLS)
    # logger.info(f"Preparando ambiente: {quantidade} arquivos antigos removidos")
    # Configurar settings personalizadas
    custom_settings = Settings()
    custom_settings.HEADLESS = False  # Executar com interface gráfica
    
    try:
        # Executar o scraper do Protheus
        with ProtheusScraper(settings=custom_settings) as scraper:
            results = scraper.run() or []  
            
            # Contar sucessos e erros
            success_count = len([r for r in results if r.get('status') == 'success'])
            error_count = len(results) - success_count
            
            # Registrar resultado do processamento
            logger.info(f"Process completed: {success_count}/{len(results)} successful submissions")
            
            # Preparar dados para email de sucesso
            completion_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            latest_report = get_latest_file(custom_settings.RESULTS_DIR)

            send_success_email(
                completion_time=completion_time,
                processed_count=len(results),
                error_count=error_count,
                report_path=str(latest_report) if latest_report else None
            )

            # fechar_web_agent()
    except Exception as e:
        # Tratar exceções específicas
        error_description, affected_count, suggested_action = handle_specific_exceptions(e, logger)
        
        # Preparar dados para email de erro
        error_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Enviar email de erro
        send_error_email(
            error_time=error_time,
            error_description=error_description,
            affected_count=affected_count,
            suggested_action=suggested_action
        )
        # fechar_web_agent()
        return 1  # Código de erro
    
    return 0  # Sucesso


# Ponto de entrada do script
if __name__ == "__main__":
    main()