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

        # 🔥 DISPARO 00:00
        if agora.minute % 2 == 0:
            hoje = agora.strftime("%d/%m/%Y")

            if ultimo_envio != hoje:
                canal = client.get_channel(CANAL_AVISOS)

                if canal:
                    await canal.send(f"""
🔥 **SVS INICIADO - {hoje}**

📊 Meta diária:
➡️ 2M VS por membro

⚔️ Foquem em:
- Coleta
- Construção
- Pesquisa
- Abate estratégico

🚨 Não esqueçam de registrar:
Use: `!vs 2.5`

Boa guerra a todos.
ΞLØ - S U P R Ξ M Ø
""")

                    print("✅ Aviso SVS enviado")

                ultimo_envio = hoje

        await asyncio.sleep(60)  # checa a cada 1 min

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
