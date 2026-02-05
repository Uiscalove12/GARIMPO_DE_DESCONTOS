import time
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from telebot import TeleBot

# --- CONFIGURAÇÕES DO SISTEMA ---
SUPABASE_URL = "https://ptdxuxnjfthemkftgeew.supabase.co"
# Chave anon funciona pois o RLS foi desativado conforme as imagens
SUPABASE_KEY = "sb_publishable_j3XhyAQ_2SX2_62o9eV7Ow_hUCxOs27"
TELEGRAM_TOKEN = "8431297763:AAFyZAr5AgQ2yo4F-xknpgd_lwNBgdDZiK8"
CHANNEL_ID = "@AchadosDoSnipers"
AMAZON_TAG = "garimposniper-20"

# Inicializando as ferramentas
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = TeleBot(TELEGRAM_TOKEN)

# Confirmação de inicialização no canal
try:
    bot.send_message(CHANNEL_ID, "🚀 **Sniper do Garimpo Online!** Monitorando ofertas com preços...")
except Exception as e:
    print(f"Erro ao conectar ao Telegram: {e}")

def buscar_ofertas():
    print("🔍 Varrendo a Amazon em busca de eletrônicos e preços...")
    url_alvo = "https://www.amazon.com.br/s?k=Eletr%C3%B4nicos&ref=nb_sb_noss_1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Cookie": "i18n-prefs=BRL; lc-acbbr=pt_BR;"
    }
    
    try:
        response = requests.get(url_alvo, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Localiza os blocos de produtos individuais (cards)
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        print(f"📦 DEBUG: Analisando {len(items)} produtos na página...")

        for item in items:
            link_tag = item.find('a', class_='a-link-normal s-no-outline', href=True)
            if not link_tag: continue
            
            href = link_tag['href']
            link_limpo = href.split('?')[0].split('ref=')[0]
            if not link_limpo.startswith('/'): continue

            try:
                # Verifica duplicata no Supabase
                check = supabase.table("ofertas_postadas").select("id").eq("url_original", link_limpo).execute()
                
                if len(check.data) == 0:
                    # --- EXTRAÇÃO DE DADOS ---
                    titulo_raw = item.find('h2')
                    titulo = titulo_raw.get_text().strip() if titulo_raw else "Produto em Oferta"
                    
                    img_raw = item.find('img', class_='s-image')
                    img_url = img_raw['src'] if img_raw else None
                    
                    # Extração de Preço
                    preco_inteiro = item.find('span', class_='a-price-whole')
                    preco_centavos = item.find('span', class_='a-price-fraction')
                    
                    if preco_inteiro:
                        valor = f"R$ {preco_inteiro.get_text().strip()},{preco_centavos.get_text().strip() if preco_centavos else '00'}"
                    else:
                        valor = "Confira o preço no site"

                    # Busca selos de desconto (ex: 20% OFF)
                    badge = item.find('span', class_='a-badge-text')
                    txt_badge = f"\n🏷️ **Destaque:** {badge.get_text().strip()}" if badge else ""

                    if not img_url or len(titulo) < 10: continue

                    link_final = f"https://www.amazon.com.br{link_limpo}?tag={AMAZON_TAG}"
                    
                    # --- FORMATAÇÃO DA MENSAGEM ---
                    texto = (
                        f"🔥 **ACHADO DO SNIPER!**\n\n"
                        f"🎯 {titulo[:110]}...\n\n"
                        f"💰 **APENAS: {valor}**{txt_badge}\n\n"
                        f"🛒 **COMPRE AQUI:** {link_final}\n\n"
                        f"🚚 *Verifique frete grátis e parcelamento no link!*"
                    )
                    
                    # Envio ao Telegram
                    bot.send_photo(CHANNEL_ID, img_url, caption=texto, parse_mode="Markdown")
                    
                    # Registro no Banco de Dados (agora com RLS Desativado)
                    supabase.table("ofertas_postadas").insert({"url_original": link_limpo}).execute()
                    print(f"✅ SUCESSO: {titulo[:30]} postado e salvo!")
                    
                    # Retorna após uma postagem para manter o ciclo de 10 min e evitar bloqueio
                    return 

            except Exception as e:
                print(f"⚠️ Erro ao processar item: {e}")
                if "429" in str(e): # Se o Telegram bloquear por velocidade
                    print("😴 Telegram pediu pausa. Encerrando ciclo atual.")
                    return
                continue
        
        # Caso a Amazon bloqueie o acesso (2 links ou menos no log)
        if len(items) == 0:
            print("⚠️ Amazon entregou página protegida (Captcha).")
            
    except Exception as e:
        print(f"❌ Erro crítico na varredura: {e}")

if __name__ == "__main__":
    while True:
        buscar_ofertas()
        # Tempo de 10 minutos para evitar bloqueio de IP da Amazon
        print("😴 Sniper aguardando 10 minutos para a próxima varredura...")
        time.sleep(600)
