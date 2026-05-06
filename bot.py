import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

# ===== DISCORD =====
TOKEN = os.getenv("DISCORD_TOKEN")

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

@client.event
async def on_ready():
    print(f'Logado como {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # 🔒 BLOQUEIA USO FORA DO CANAL VS
    if message.content.startswith("!vs"):

        if message.channel.id != int(os.getenv("CANAL_VS")):
            return

        try:
            valor = float(message.content.split(" ")[1])
            usuario = str(message.author)
            data = datetime.now().strftime("%d/%m/%Y")

            sheet.append_row([data, usuario, valor])

            await message.channel.send(f"✅ VS registrado: {valor}M")

        except:
            await message.channel.send("❌ Use: !vs 2.5")

client.run(TOKEN)
