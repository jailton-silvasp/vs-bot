import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json
import asyncio
import pytz

# ===== DISCORD =====
TOKEN = os.getenv("DISCORD_TOKEN")

CANAL_VS = os.getenv("CANAL_VS")
CANAL_AVISOS = os.getenv("CANAL_AVISOS")

if CANAL_VS:
    CANAL_VS = int(CANAL_VS)

if CANAL_AVISOS:
    CANAL_AVISOS = int(CANAL_AVISOS)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ===== GOOGLE =====
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client_gspread = gspread.authorize(creds)

sheet = client_gspread.open("Controle VS").sheet1

# ===== TIMEZONE BRASIL =====
tz = pytz.timezone("America/Sao_Paulo")

# ===== CONTROLE PRA NÃO DUPLICAR =====
ultimo_envio = None

@client.event
async def on_ready():
    print(f'Logado como {client.user}')
    client.loop.create_task(rotina_svs())

# ===== ROTINA AUTOMÁTICA =====
async def rotina_svs():
    global ultimo_envio

    await client.wait_until_ready()

    while not client.is_closed():
        agora = datetime.now(tz)

        if agora.hour == 0 and agora.minute == 0:
            hoje = agora.strftime("%d/%m/%Y")

            if ultimo_envio != hoje:
                canal = client.get_channel(CANAL_AVISOS)

                if canal:
                    dia = agora.weekday()

                    mensagens = {

                        0: f"""📅 **Dia 1 – Expansão do Abrigo ({hoje})**

🏗 Construção | 📜 Medalhas | 🔬 Pesquisa  
⚙️ Use aceleradores de construção e pesquisa  
💰 Coleta o dia inteiro  

🚨 Use: !vs 2.5
""",

                        1: f"""📅 **Dia 2 – Iniciativa de Heróis ({hoje})**

📡 Radar | 🎖 Recrutamento Prime  
🧩 Fragmentos | 🎯 Equipamentos  

💡 Dica: iniciar treino antes do reset
""",

                        2: f"""📅 **Dia 3 – Progresso ({hoje})**

🚚 Caminhões S | 🕶 Missões laranja  
🪖 Treinamento de tropas  
⚙️ Aceleradores apenas treino
""",

                        3: f"""📅 **Dia 4 – Especialista em Armas ({hoje})**

📡 Radar | 💥 Rally Boomer  
🧟 Zumbis | 🧰 Chips  
⚙️ Todos aceleradores liberados
""",

                        4: f"""📅 **Dia 5 – Crescimento ({hoje})**

🧩 Fragmentos | 🔋 Núcleos  
📜 Medalhas | 🎯 Equipamentos  

💡 Use tudo que sobrou
""",

                        5: f"""📅 **Dia 6 – PvP / Guerra ({hoje})**

🚚 Caminhões S  
🎯 Combate | 💀 Perdas contam  

🛡 Use escudo se necessário
""",

                        6: f"""🔥 **SVS ENCERRADO ({hoje})**

💪 Cure tropas  
📊 Reorganize seu poder  
⚔️ Prepare-se para próxima semana
"""
                    }

                    mensagem = mensagens.get(dia)

                    if mensagem:
                        await canal.send(mensagem)
                        print(f"✅ SVS Dia {dia+1} enviado")

                ultimo_envio = hoje

        await asyncio.sleep(60)

# ===== VS =====
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if CANAL_VS and message.channel.id != CANAL_VS:
        return

    if message.content.startswith("!vs"):
        try:
            valor = float(message.content.split(" ")[1])
            usuario = str(message.author)
            data = datetime.now(tz).strftime("%d/%m/%Y")

            sheet.append_row([data, usuario, valor])

            await message.channel.send(f"✅ VS registrado: {valor}M")
        except:
            await message.channel.send("❌ Use: !vs 2.5")

client.run(TOKEN)
