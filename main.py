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

# Linha de teste imediato para confirmar conexão
try:
    bot.send_message(CHANNEL_ID, "🚀 **Sniper do Garimpo Atualizado!** Iniciando varredura em Eletrônicos...")
except Exception as e:
    print(f"Erro ao enviar mensagem inicial: {e}")

def buscar_ofertas():
    print("🔍 Varrendo a categoria de Eletrônicos...")
    # URL que você escolheu (com o disfarce de busca)
    url_alvo = "https://www.amazon.com.br/s?k=Eletr%C3%B4nicos&ref=nb_sb_noss_1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": "i18n-prefs=BRL; lc-acbbr=pt_BR;"
    }
    
    try:
        response = requests.get(url_alvo, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pega todos os links da página para análise profunda
        links_produtos = soup.find_all('a', href=True)
        print(f"📦 DEBUG: Analisando {len(links_produtos)} links na página...")

        for link in links_produtos:
            href = link['href']
            # Filtra links de produtos reais (/dp/ ou /gp/)
            if '/dp/' in href or '/gp/product/' in href:
                # Limpa o link para evitar rastreadores da Amazon
                link_limpo = href.split('?')[0].split('ref=')[0]
                
                if not link_limpo.startswith('/'): continue

                try:
                    # Verifica se já postamos esse link no Supabase
                    check = supabase.table("ofertas_postadas").select("id").eq("url_original", link_limpo).execute()
                    
                    if len(check.data) == 0:
                        # Extrai título e imagem
                        img_tag = link.find('img') or link.parent.find('img')
                        titulo = img_tag.get('alt', 'Oferta de Eletrônico') if img_tag else "Oferta Especial"
                        img_url = img_tag['src'] if img_tag else None
                        
                        if not img_url or len(titulo) < 10: continue

                        link_final = f"https://www.amazon.com.br{link_limpo}?tag={AMAZON_TAG}"
                        texto = f"🔥 **ACHADO DO SNIPER!**\n\n🎯 {titulo}\n\n🛒 **COMPRE AQUI:** {link_final}"
                        
                        # Posta no Telegram
                        bot.send_photo(CHANNEL_ID, img_url, caption=texto, parse_mode="Markdown")
                        
                        # Salva na sua tabela 'ofertas_postadas' no Supabase
                        supabase.table("ofertas_postadas").insert({"url_original": link_limpo}).execute()
                        print(f"✅ SUCESSO: {titulo[:30]} postado!")
                        
                        # Posta uma e encerra para o próximo ciclo (evita spam e bloqueio)
                        return 
                except Exception as e:
                    print(f"⚠️ Erro ao processar item: {e}")
                    continue
        
        if len(links_produtos) < 10:
            print("⚠️ Amazon entregou página protegida. Vamos aguardar o próximo ciclo.")
            
    except Exception as e:
        print(f"❌ Erro na varredura: {e}")

if __name__ == "__main__":
    while True:
        buscar_ofertas()
        # Tempo de descanso maior (10 minutos) para evitar bloqueio de IP
        print("😴 Sniper em modo de espera por 10 minutos...")
        time.sleep(600)
