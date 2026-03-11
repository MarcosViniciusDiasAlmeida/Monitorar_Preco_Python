import smtplib
from email.message import EmailMessage
import security
from datetime import datetime

def send_email(destinatario: str, assunto: str, mensagem_html: str, mensagem_texto: str = None):
    """
    Envia e-mail com versão HTML e texto puro (fallback).
    Inclui timestamp no corpo da mensagem.
    """
    # Obtém a data/hora atual
    agora = datetime.now()
    timestamp = agora.strftime("%d/%m/%Y %H:%M:%S")

    # Se não foi fornecida versão texto, cria uma básica
    if mensagem_texto is None:
        mensagem_texto = f"Mensagem enviada em {timestamp}\n\nConteúdo HTML não suportado."

    # Adiciona timestamp ao HTML (insere antes do fechamento do body)
    mensagem_html_com_timestamp = mensagem_html.replace(
        '</body>',
        f'<p style="color: #999; font-size: 11px; text-align: center;">E-mail enviado em {timestamp}</p>\n</body>'
    )

    # Configuração do servidor SMTP do Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(security.username_email, security.password_email)

    # Cria a mensagem
    email_msg = EmailMessage()
    email_msg['From'] = security.username_email
    email_msg['To'] = destinatario
    email_msg['Subject'] = assunto

    # Adiciona as duas versões: texto puro e HTML
    email_msg.set_content(mensagem_texto)
    email_msg.add_alternative(mensagem_html_com_timestamp, subtype='html')

    # Envia
    server.send_message(email_msg)
    server.quit()

    print("E-mail enviado com sucesso!")

# Bloco de teste (opcional)
if __name__ == '__main__':
    # Exemplo de teste
    titulo = 'Tênis Fila Racer Speedzone'
    preco_original = 'R$ 549,00'
    preco_atual = 'R$ 479,00'
    status = 'Ainda acima de R$ 400,00'
    link = 'https://produto.mercadolivre.com.br/...'

    html_teste = f"""
    <h1>{titulo}</h1>
    <p>Original: {preco_original}</p>
    <p>Atual: <strong>{preco_atual}</strong></p>
    <p>{status}</p>
    <a href="{link}">Ver produto</a>
    """
    texto_teste = f"{titulo}\nOriginal: {preco_original}\nAtual: {preco_atual}\n{status}\nLink: {link}"

    send_email(
        destinatario=security.username_email,
        assunto='Teste do monitor de preços',
        mensagem_html=html_teste,
        mensagem_texto=texto_teste
    )