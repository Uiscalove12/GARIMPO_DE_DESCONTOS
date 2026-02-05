import time
import requests
from bs4 import BeautifulSoup
from supabase import create_client
from telebot import TeleBot

# --- CONFIGURAÇÕES DO SISTEMA ---
SUPABASE_URL = "https://ptdxuxnjfthemkftgeew.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB0ZHh1eG5qZnRoZW1rZnRnZWV3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2OTk4NDE1NCwiZXhwIjoyMDg1NTYwMTU0fQ.K70krFARzKgUdB_MHaTLlJtqK-1MGgNTjPdjWTrBXr8"
TELEGRAM_TOKEN = "8431297763:AAFyZAr5AgQ2yo4F-xknpgd_lwNBgdDZiK8"
CHANNEL_ID = "@AchadosDoSnipers"
AMAZON_TAG = "garimposniper-20"

# Inicializando as ferramentas
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = TeleBot(TELEGRAM_TOKEN)
# Linha de teste imediato
bot.send_message(CHANNEL_ID, "🚀 **Sniper do Garimpo Online!** Monitorando ofertas...")

def buscar_ofertas():
    print("🔍 Varrendo a Amazon com busca profunda...")
    # URL de ofertas mais "aberta"
    url_alvo = "https://www.amazon.com.br/deals?ref_=nav_cs_gb"
    
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Cookie": "i18n-prefs=BRL; lc-acbbr=pt_BR;" # Isso diz à Amazon que você é um brasileiro real
}
    
    try:
        response = requests.get(url_alvo, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tenta pegar os cards de oferta específicos da página /deals
        links_produtos = soup.find_all('a', {'class': 'a-link-normal'}, href=True)
        print(f"📦 DEBUG: Analisando {len(links_produtos)} links de ofertas...")

        for link in links_produtos:
            href = link['href']
            # Filtra links que contenham o padrão de produto da Amazon (/dp/ ou /gp/product/)
            if '/dp/' in href or '/gp/product/' in href:
                link_limpo = href.split('?')[0].split('ref=')[0]
                
                # Evita links incompletos
                if not link_limpo.startswith('/'): continue

                try:
                    # Verifica no seu Supabase (que já está OK!)
                    check = supabase.table("ofertas_postadas").select("id").eq("url_original", link_limpo).execute()
                    
                    if len(check.data) == 0:
                        # Tenta pegar o título do link ou da imagem dentro dele
                        titulo = link.get_text().strip() or (link.find('img')['alt'] if link.find('img') else "Oferta Especial")
                        img_url = link.find('img')['src'] if link.find('img') else None
                        
                        if len(titulo) < 10 or not img_url: continue # Pula lixo

                        link_final = f"https://www.amazon.com.br{link_limpo}?tag={AMAZON_TAG}"
                        texto = f"🔥 **ACHADO DO SNIPER!**\n\n🎯 {titulo}\n\n🛒 **COMPRE AQUI:** {link_final}"
                        
                        bot.send_photo(CHANNEL_ID, img_url, caption=texto, parse_mode="Markdown")
                        
                        # Salva no banco de dados
                        supabase.table("ofertas_postadas").insert({"url_original": link_limpo}).execute()
                        print(f"✅ POSTADO: {titulo[:30]}...")
                        return # Posta um e aguarda o próximo ciclo de 60s
                except:
                    continue
        
        print("⚠️ Nenhuma oferta nova qualificada nesta varredura.")
    except Exception as e:
        print(f"❌ Erro na varredura: {e}")

# Loop infinito: roda a cada 1 hora (3600 segundos)
if __name__ == "__main__":
    while True:
        buscar_ofertas()

        time.sleep(60)
