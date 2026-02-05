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
    print("🔍 Varrendo a página de Ofertas Mobile...")
    # URL Mobile que você sugeriu
    url_alvo = "https://www.amazon.com.br/gp/aw/gb/?ref_=navm_cs_gb"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Connection": "keep-alive",
        "Cookie": "i18n-prefs=BRL; lc-acbbr=pt_BR;"
    }
    
    try:
        response = requests.get(url_alvo, headers=headers, timeout=25)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Na versão mobile, os itens costumam ficar em links com essa classe
        items = soup.find_all('a', href=True)
        print(f"📦 DEBUG: Analisando {len(items)} possíveis links de oferta...")

        postados = 0
        for item in items:
            href = item['href']
            # Filtra apenas produtos reais
            if '/dp/' in href or '/gp/product/' in href:
                link_limpo = href.split('?')[0].split('ref=')[0]
                if not link_limpo.startswith('/'): continue

                try:
                    # Verifica duplicata (RLS Desativado permite isso)
                    check = supabase.table("ofertas_postadas").select("id").eq("url_original", link_limpo).execute()
                    
                    if len(check.data) == 0:
                        # Extração adaptada para Mobile
                        img_tag = item.find('img')
                        titulo = img_tag.get('alt', 'Oferta Especial') if img_tag else "Produto em Oferta"
                        img_url = img_tag['src'] if img_tag else None
                        
                        # Preço em mobile costuma estar em tags de texto simples
                        valor = "Confira no link"
                        preco_txt = item.get_text()
                        if "R$" in preco_txt:
                            # Tenta extrair o valor aproximado do texto do link
                            valor = "R$ " + preco_txt.split("R$")[1].split()[0]

                        if not img_url or len(titulo) < 10: continue

                        link_final = f"https://www.amazon.com.br{link_limpo}?tag={AMAZON_TAG}"
                        
                        texto = (
                            f"🔥 **ACHADO MOBILE DO SNIPER!**\n\n"
                            f"🎯 {titulo[:110]}...\n\n"
                            f"💰 **VALOR: {valor}**\n\n"
                            f"🛒 **COMPRE AQUI:** {link_final}\n\n"
                            f"🚚 *Frete grátis para membros Prime!*"
                        )
                        
                        bot.send_photo(CHANNEL_ID, img_url, caption=texto, parse_mode="Markdown")
                        
                        # Salva no Supabase
                        supabase.table("ofertas_postadas").insert({"url_original": link_limpo}).execute()
                        print(f"✅ SUCESSO: {titulo[:30]}")
                        
                        postados += 1
                        if postados >= 3: return # Posta 3 e descansa 10 min
                        time.sleep(5) 

                except Exception as e:
                    print(f"⚠️ Erro no item: {e}")
                    continue
        
        if len(items) < 20:
            print("⚠️ Amazon ainda bloqueando. Tentando novamente no próximo ciclo.")

    except Exception as e:
        print(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    while True:
        buscar_ofertas()
        print("😴 Sniper em descanso de 10 minutos...")
        time.sleep(600)
