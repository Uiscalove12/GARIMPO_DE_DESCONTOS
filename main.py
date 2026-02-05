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
# Linha de teste imediato
bot.send_message(CHANNEL_ID, "🚀 **Sniper do Garimpo Online!** Monitorando ofertas...")

def buscar_ofertas():
def buscar_ofertas():
    print("🔍 Varrendo a Amazon em busca de descontos...")
    # Usando a URL de promoções que é mais estável
    url_alvo = "https://www.amazon.com.br/promocoes"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9"
    }
    
    try:
        response = requests.get(url_alvo, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Seletores variados para garantir que pegue o produto
        itens = soup.find_all('div', {'data-testid': 'grid-desktop-card'}) or \
                soup.find_all('div', {'class': 's-result-item'})
        
        print(f"📦 Itens detectados na página: {len(itens)}")

        for item in itens:
            try:
                img_tag = item.find('img')
                link_tag = item.find('a')
                
                if not img_tag or not link_tag:
                    continue

                titulo = img_tag.get('alt', 'Produto sem título')
                link_limpo = link_tag['href'].split('?')[0]
                img_url = img_tag['src']
                
                # Verifica no Supabase
                check = supabase.table("ofertas_postadas").select("id").eq("url_original", link_limpo).execute()
                
                if len(check.data) == 0:
                    link_final = f"https://www.amazon.com.br{link_limpo}?tag={AMAZON_TAG}" if link_limpo.startswith('/') else f"{link_limpo}?tag={AMAZON_TAG}"
                    
                    texto = f"🔥 **ACHADO DO SNIPER!**\n\n🎯 {titulo}\n\n🛒 **COMPRE AQUI:** {link_final}"
                    bot.send_photo(CHANNEL_ID, img_url, caption=texto, parse_mode="Markdown")
                    
                    # Salva no Supabase
                    supabase.table("ofertas_postadas").insert({"url_original": link_limpo}).execute()
                    print(f"✅ Postado: {titulo}")
                    return # Posta um por vez para evitar spam inicial
            except Exception as e:
                continue
    except Exception as e:
        print(f"❌ Erro na varredura: {e}")

# Loop infinito: roda a cada 1 hora (3600 segundos)
if __name__ == "__main__":
    while True:
        buscar_ofertas()

        time.sleep(60)



