import time
import requests
import random
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

# Confirmação de início
print("🚀 Sniper configurado para as novas categorias!")

def buscar_ofertas():
    # Lista com os seus 4 links específicos (nodos de categoria)
    urls_categorias = [
        "https://www.amazon.com.br/b/?_encoding=UTF8&node=207659002011",
        "https://www.amazon.com.br/b/?_encoding=UTF8&node=207658989011",
        "https://www.amazon.com.br/b/?_encoding=UTF8&node=207744280011",
        "https://www.amazon.com.br/b/?_encoding=UTF8&node=207658990011"
    ]
    
    url_alvo = random.choice(urls_categorias)
    print(f"📡 Varrendo categoria selecionada: {url_alvo}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Cookie": "i18n-prefs=BRL; lc-acbbr=pt_BR;"
    }
    
    try:
        response = requests.get(url_alvo, headers=headers, timeout=25)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links_produtos = soup.find_all('a', href=True)
        print(f"📦 DEBUG: Analisando {len(links_produtos)} links na página...")

        postados_neste_ciclo = 0

        for link in links_produtos:
            # Limite de 3 postagens por ciclo para ser eficiente e seguro
            if postados_neste_ciclo >= 3:
                return

            href = link['href']
            if '/dp/' in href or '/gp/product/' in href:
                link_limpo = href.split('?')[0].split('ref=')[0]
                
                if not link_limpo.startswith('/'): continue

                try:
                    # Verifica se já existe no Supabase
                    check = supabase.table("ofertas_postadas").select("id").eq("url_original", link_limpo).execute()
                    
                    if len(check.data) == 0:
                        img_tag = link.find('img') or link.parent.find('img')
                        titulo = img_tag.get('alt', 'Oferta Especial Amazon').strip() if img_tag else "Produto em Oferta"
                        img_url = img_tag.get('src') if img_tag else None
                        
                        if not img_url or len(titulo) < 12: continue

                        link_final = f"https://www.amazon.com.br{link_limpo}?tag={AMAZON_TAG}"
                        
                        texto = (
                            f"🔥 **ACHADO DO SNIPER!**\n\n"
                            f"🎯 {titulo[:110]}...\n\n"
                            f"🛒 **COMPRE AQUI:** {link_final}\n\n"
                            f"🚚 Verifique frete grátis no link!"
                        )
                        
                        bot.send_photo(CHANNEL_ID, img_url, caption=texto, parse_mode="Markdown")
                        
                        # Salva no Supabase
                        supabase.table("ofertas_postadas").insert({"url_original": link_limpo}).execute()
                        print(f"✅ SUCESSO: {titulo[:30]} postado!")
                        
                        postados_neste_ciclo += 1
                        time.sleep(7) # Pequena pausa entre fotos
                        
                except Exception as e:
                    print(f"⚠️ Erro ao processar item: {e}")
                    continue
        
        if len(links_produtos) < 15:
            print("⚠️ Amazon entregou página protegida ou vazia.")
            
    except Exception as e:
        print(f"❌ Erro na varredura: {e}")

if __name__ == "__main__":
    while True:
        buscar_ofertas()
        # Tempo de 10 minutos (600 segundos)
        print("😴 Sniper em modo de espera por 10 minutos...")
        time.sleep(600)
