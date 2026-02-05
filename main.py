import time
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from telebot import TeleBot

# --- CONFIGURAÇÕES DO SISTEMA ---
SUPABASE_URL = "https://ptdxuxnjfthemkftgeew.supabase.co"
SUPABASE_KEY = "sb_publishable_j3XhyAQ_2SX2_62o9eV7Ow_hUCxOs27"
TELEGRAM_TOKEN = "8431297763:AAFyZAr5AgQ2yo4F-xknpgd_lwNBgdDZiK8"
CHANNEL_ID = "@AchadosDoSnipers"
AMAZON_TAG = "garimposniper-20"

# Inicializando as ferramentas
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = TeleBot(TELEGRAM_TOKEN)

def buscar_ofertas():
    print("🔍 Varrendo a Amazon em busca de descontos...")
    url_alvo = "https://www.amazon.com.br/gp/goldbox"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url_alvo, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Buscando os cards de produtos (seletor padrão da Amazon)
        itens = soup.find_all('div', {'data-testid': 'grid-desktop-card'})

        for item in itens:
            try:
                # Extraindo dados básicos
                titulo = item.find('img')['alt']
                link_limpo = item.find('a')['href'].split('?')[0]
                img_url = item.find('img')['src']
                
                # 1. Verifica no Supabase se é oferta repetida
                check = supabase.table("ofertas_postadas").select("id").eq("url_original", link_limpo).execute()
                
                if len(check.data) == 0:
                    # 2. Gera o Link com sua ID de Afiliado
                    link_final = f"https://www.amazon.com.br{link_limpo}?tag={AMAZON_TAG}" if link_limpo.startswith('/') else f"{link_limpo}?tag={AMAZON_TAG}"
                    
                    # 3. Monta e envia a mensagem
                    texto = f"🔥 **ACHADO DO SNIPER!**\n\n🎯 {titulo}\n\n🛒 **COMPRE AQUI:** {link_final}"
                    bot.send_photo(CHANNEL_ID, img_url, caption=texto, parse_mode="Markdown")
                    
                    # 4. Salva no Banco de Dados para evitar duplicidade
                    supabase.table("ofertas_postadas").insert({"url_original": link_limpo}).execute()
                    print(f"✅ Postado com sucesso: {titulo}")
                    time.sleep(5) # Evita bloqueio do Telegram
            except Exception as e:
                continue
    except Exception as e:
        print(f"❌ Erro na varredura: {e}")

# Loop infinito: roda a cada 1 hora (3600 segundos)
if __name__ == "__main__":
    while True:
        buscar_ofertas()
        time.sleep(3600)