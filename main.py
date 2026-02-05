import time
import requests
import random
from bs4 import BeautifulSoup
from supabase import create_client
from telebot import TeleBot

# --- CONFIGURAÇÕES ---
SUPABASE_URL = "https://ptdxuxnjfthemkftgeew.supabase.co"
SUPABASE_KEY = "sb_publishable_j3XhyAQ_2SX2_62o9eV7Ow_hUCxOs27"
TELEGRAM_TOKEN = "8431297763:AAFyZAr5AgQ2yo4F-xknpgd_lwNBgdDZiK8"
CHANNEL_ID = "@AchadosDoSnipers"
AMAZON_TAG = "garimposniper-20"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = TeleBot(TELEGRAM_TOKEN)

def obter_identidade():
    """Retorna um User-Agent e um Proxy aleatório"""
    agentes = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]
    return {"User-Agent": random.choice(agentes)}

def buscar_ofertas():
    print("🎭 Mudando identidade e iniciando busca...")
    # Alternamos entre a URL mobile e uma URL de busca comum para despistar
    urls = [
        "https://www.amazon.com.br/gp/aw/gb/?ref_=navm_cs_gb",
        "https://www.amazon.com.br/s?k=ofertas+do+dia&ref=nb_sb_noss"
    ]
    url_alvo = random.choice(urls)
    
    headers = obter_identidade()
    headers.update({
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com.br/"
    })

    try:
        # Tentativa de acesso (usando timeout maior para proxies lentos)
        response = requests.get(url_alvo, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Busca por links de produtos (/dp/ ou /gp/product/)
        links = soup.find_all('a', href=True)
        produtos_encontrados = [l for l in links if '/dp/' in l['href'] or '/gp/product/' in l['href']]
        
        print(f"📦 DEBUG: Encontrados {len(produtos_encontrados)} produtos potenciais.")

        postados_neste_ciclo = 0
        for prod in produtos_encontrados:
            if postados_neste_ciclo >= 3: break # Limite de 3 para não ser bloqueado

            href = prod['href']
            link_limpo = href.split('?')[0].split('ref=')[0]
            if not link_limpo.startswith('/'): continue

            # Verifica no Supabase
            check = supabase.table("ofertas_postadas").select("id").eq("url_original", link_limpo).execute()
            
            if len(check.data) == 0:
                img_tag = prod.find('img')
                titulo = img_tag.get('alt', 'Oferta Incrível') if img_tag else "Produto em Oferta"
                img_url = img_tag['src'] if img_tag else None
                
                if not img_url or len(titulo) < 15: continue

                link_final = f"https://www.amazon.com.br{link_limpo}?tag={AMAZON_TAG}"
                texto = (
                    f"🎯 **{titulo[:90]}...**\n\n"
                    f"🔥 Confira o preço especial no link abaixo!\n"
                    f"🛒 **COMPRE AQUI:** {link_final}\n\n"
                    f"🚚 Frete Grátis Prime ✅"
                )

                bot.send_photo(CHANNEL_ID, img_url, caption=texto, parse_mode="Markdown")
                
                # Salva no Banco
                supabase.table("ofertas_postadas").insert({"url_original": link_limpo}).execute()
                print(f"✅ POSTADO: {titulo[:30]}")
                postados_neste_ciclo += 1
                time.sleep(random.randint(5, 10)) # Pausa humana entre postagens

        if postados_neste_ciclo == 0:
            print("⚠️ Nenhuma oferta nova qualificada (ou todas já foram postadas).")

    except Exception as e:
        print(f"❌ Erro na varredura: {e}")

if __name__ == "__main__":
    while True:
        buscar_ofertas()
        # Tempo de espera aleatório entre 10 e 20 minutos
        minutos = random.randint(10, 20)
        print(f"😴 Descansando por {minutos} minutos...")
        time.sleep(minutos * 60)
