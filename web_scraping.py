from bs4 import BeautifulSoup
import requests
import send_email as email
import security

def extrair_preco(soup, tipo='atual'):
    """
    Função auxiliar para extrair preços do Mercado Livre.
    tipo = 'atual' (com desconto) ou 'original' (riscado)
    Retorna o preço como float ou None se não encontrar.
    """
    preco_text = None

    if tipo == 'atual':
        # Tenta encontrar o container do preço com desconto (com centavos sobrescritos)
        container = soup.find('div', class_='andes-money-amount--cents-superscript')
        if container:
            fracao = container.find('span', class_='andes-money-amount__fraction')
            centavos = container.find('span', class_='andes-money-amount__cents')
            if fracao:
                preco_text = fracao.get_text().strip()
                if centavos:
                    preco_text += '.' + centavos.get_text().strip()
        else:
            # Fallback: pega o último preço da página (segundo elemento)
            tags = soup.find_all('span', class_='andes-money-amount__fraction')
            if len(tags) >= 2:
                preco_text = tags[1].get_text().strip()
            elif len(tags) == 1:
                preco_text = tags[0].get_text().strip()

    elif tipo == 'original':
        # Tenta encontrar o preço original (riscado)
        container_original = soup.find('div', class_='andes-money-amount--previous')
        if container_original:
            fracao = container_original.find('span', class_='andes-money-amount__fraction')
            centavos = container_original.find('span', class_='andes-money-amount__cents')
            if fracao:
                preco_text = fracao.get_text().strip()
                if centavos:
                    preco_text += '.' + centavos.get_text().strip()
        else:
            # Se não achar, pega o primeiro preço (pode ser o original)
            tags = soup.find_all('span', class_='andes-money-amount__fraction')
            if len(tags) >= 1:
                preco_text = tags[0].get_text().strip()

    if preco_text:
        # Limpa e converte para float
        preco_text = preco_text.replace('.', '')  # remove pontos de milhar
        preco_text = preco_text.replace(',', '.')  # troca vírgula decimal
        try:
            return float(preco_text)
        except:
            return None
    return None

def monitoramento(EnviarEmail: bool):

    URL = 'https://produto.mercadolivre.com.br/MLB-5375843056-tnis-fila-racer-speedzone-feminino-corrida-original-novo-_JM?attributes=COLOR_SECONDARY_COLOR%3AQlJBTkNPL1BSQVRBL0NJTlpB&matt_tool=38524122#origin=share&sid=share&action=whatsapp'

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    site = requests.get(URL, headers=headers)
    soup = BeautifulSoup(site.content, 'html.parser')

    # --- TÍTULO ---
    title_tag = soup.find('h1', class_='ui-pdp-title')
    title = title_tag.get_text().strip() if title_tag else "Título não encontrado"

    # --- PREÇOS ---
    preco_original = extrair_preco(soup, tipo='original')
    preco_atual = extrair_preco(soup, tipo='atual')

    # Se não conseguir o original, usa o atual como fallback
    if preco_original is None:
        preco_original = preco_atual

    if preco_atual is None:
        print("Não foi possível encontrar o preço atual.")
        return

    # --- CONSTRUÇÃO DA MENSAGEM HTML ---
    preco_original_str = f"R$ {preco_original:.2f}".replace('.', ',')
    preco_atual_str = f"R$ {preco_atual:.2f}".replace('.', ',')
    diferenca = preco_atual - 400
    diferenca_str = f"R$ {abs(diferenca):.2f}".replace('.', ',')

    # Define a cor e o ícone baseado no status
    if preco_atual < 400:
        status_cor = "#2ecc71"  # verde
        status_icone = "🔥"
        status_texto = f"Está ABAIXO de R$ 400,00! Corra para comprar!"
    else:
        status_cor = "#e67e22"  # laranja
        status_icone = "⚠️"
        status_texto = f"Ainda está ACIMA de R$ 400,00 (diferença de {diferenca_str})"

    # Monta o HTML
    mensagem_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Monitor de Preços</title>
    </head>
    <body style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto; background-color: #f9f9f9;">
        <div style="background-color: white; border-radius: 10px; padding: 25px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h1 style="color: #333; margin-top: 0;">{title}</h1>
            
            <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-radius: 8px;">
                <p style="font-size: 18px; margin: 10px 0;">
                    <span style="color: #666;">Preço original:</span> 
                    <span style="text-decoration: line-through; color: #999; font-size: 20px;">{preco_original_str}</span>
                </p>
                <p style="font-size: 18px; margin: 10px 0;">
                    <span style="color: #666;">Preço promocional:</span> 
                    <span style="color: #2ecc71; font-size: 32px; font-weight: bold;">{preco_atual_str}</span>
                </p>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; background-color: #fff3e0; border-left: 5px solid {status_cor}; border-radius: 5px;">
                <p style="font-size: 18px; margin: 0; color: {status_cor};">
                    {status_icone} <strong>{status_texto}</strong>
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="{URL}" style="background-color: #3498db; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-size: 16px; display: inline-block;">🔗 Ver produto no Mercado Livre</a>
            </div>
            
            <p style="color: #999; font-size: 12px; text-align: center; margin-top: 30px;">
                Este é um e-mail automático do seu monitor de preços.
            </p>
        </div>
    </body>
    </html>
    """

    # Versão texto puro (fallback)
    mensagem_texto = f"""
    {title}

    Preço original (bruto): {preco_original_str}
    Preço promocional (atual): {preco_atual_str}
    {status_texto}

    Link: {URL}
    """

    # Exibe no terminal para debug
    print(f"Título: {title}")
    print(f"Preço original: {preco_original_str}")
    print(f"Preço atual: {preco_atual_str}")

    # --- ENVIO DE E-MAIL ---
    if EnviarEmail:
        if preco_atual < 400:
            email.send_email(
                destinatario=security.username_email,
                assunto=f'🔥 PROMOÇÃO! {title}',
                mensagem_html=mensagem_html,
                mensagem_texto=mensagem_texto
            )
            print("E-mail de promoção enviado!")
        else:
            # Se quiser receber atualizações mesmo sem promoção, descomente:
            email.send_email(
                destinatario=security.username_email,
                assunto=f'📊 Atualização de preço - {title}',
                mensagem_html=mensagem_html,
                mensagem_texto=mensagem_texto
            )
            print("E-mail de atualização enviado (sem promoção).")
    else:
        print("Envio de e-mail não autorizado.")

if __name__ == '__main__':
    monitoramento(EnviarEmail=True)