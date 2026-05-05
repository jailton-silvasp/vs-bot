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

CANAL_VS = int(os.getenv("CANAL_VS"))
CANAL_AVISOS = int(os.getenv("CANAL_AVISOS"))

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

# ===== TIMEZONE =====
tz = pytz.timezone("America/Sao_Paulo")

# ===== CONTROLE =====
ultimo_envio = None
ultimo_ranking = None
ultimo_alerta = None


# =========================================
# 🏆 RANKING
# =========================================
async def enviar_ranking():
    canal = client.get_channel(CANAL_AVISOS)

    if not canal:
        print("❌ Canal não encontrado")
        return

    dados = sheet.get_all_records()
    hoje = datetime.now(tz).strftime("%d/%m/%Y")

    ranking = {}

    for linha in dados:
        if linha['Data'] == hoje:
            user = linha['Usuário']
            try:
                vs = float(str(linha['VS']).replace(",", "."))
            except:
                continue

            ranking[user] = ranking.get(user, 0) + vs

    ranking_ordenado = sorted(ranking.items(), key=lambda x: x[1], reverse=True)

    mensagem = "🏆 **RANKING VS DO DIA**\n\n"

    if ranking_ordenado:
        for i, (user, vs) in enumerate(ranking_ordenado[:10], start=1):
            mensagem += f"{i}. {user} — {round(vs,2)}M\n"
    else:
        mensagem += "Sem registros hoje."

    await canal.send(mensagem)


# =========================================
# ⚠️ ALERTA META
# =========================================
async def verificar_meta():
    canal = client.get_channel(CANAL_AVISOS)

    if not canal:
        return

    dados = sheet.get_all_records()
    hoje = datetime.now(tz).strftime("%d/%m/%Y")

    ranking = {}

    for linha in dados:
        if linha['Data'] == hoje:
            user = linha['Usuário']
            try:
                vs = float(str(linha['VS']).replace(",", "."))
            except:
                continue

            ranking[user] = ranking.get(user, 0) + vs

    nao_bateram = [u for u, v in ranking.items() if v < 2]

    if nao_bateram:
        mensagem = "⚠️ **NÃO BATERAM 2M HOJE:**\n\n"

        for user in nao_bateram:
            mensagem += f"- {user}\n"

        await canal.send(mensagem)
    else:
        print("✅ Todos bateram meta ou sem dados")


# =========================================
# 🚀 ROTINA PRINCIPAL
# =========================================
async def rotina_svs():
    global ultimo_envio, ultimo_ranking, ultimo_alerta

    await client.wait_until_ready()

    while not client.is_closed():
        agora = datetime.now(tz)
        hoje = agora.strftime("%d/%m/%Y")

        canal = client.get_channel(CANAL_AVISOS)

        if canal:

            # 🔥 00:00 SVS
            if agora.hour == 0 and agora.minute == 0:
                if ultimo_envio != hoje:

                    dia = agora.weekday()

                    mensagens = {
                        0: f"📅 Dia 1 – Expansão ({hoje})\n🏗 Construção | 🔬 Pesquisa | 💰 Coleta",
                        1: f"📅 Dia 2 – Heróis ({hoje})\n📡 Radar | 🎖 Recrutamento | 🧩 Fragmentos",
                        2: f"📅 Dia 3 – Tropas ({hoje})\n🪖 Treino | 🚚 Missões S",
                        3: f"📅 Dia 4 – Armas ({hoje})\n💥 Rally | 🧟 Zumbis",
                        4: f"📅 Dia 5 – Crescimento ({hoje})\n🧩 Fragmentos | 🔋 Núcleos",
                        5: f"📅 Dia 6 – Guerra ({hoje})\n⚔️ PvP | 💀 Perdas",
                        6: f"🔥 SVS ENCERRADO ({hoje})\n💪 Recuperação"
                    }

                    await canal.send(mensagens.get(dia))
                    print("✅ SVS enviado")

                    ultimo_envio = hoje

            # 🏆 23:55 Ranking
            if agora.hour == 23 and agora.minute == 55:
                if ultimo_ranking != hoje:
                    await enviar_ranking()
                    print("🏆 Ranking enviado")
                    ultimo_ranking = hoje

            # ⚠️ 23:57 Meta
            if agora.hour == 23 and agora.minute == 57:
                if ultimo_alerta != hoje:
                    await verificar_meta()
                    print("⚠️ Alerta enviado")
                    ultimo_alerta = hoje

        await asyncio.sleep(60)


# =========================================
# 🎮 VS COMANDO
# =========================================
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == CANAL_VS:

        if message.content.startswith("!vs"):
            try:
                valor = float(message.content.split(" ")[1])

                # 🔥 AQUI ESTÁ A MUDANÇA PRINCIPAL
                usuario = message.author.display_name or message.author.name

                data = datetime.now(tz).strftime("%d/%m/%Y")

                sheet.append_row([data, usuario, valor])

                await message.channel.send(f"✅ VS registrado: {valor}M")

            except:
                await message.channel.send("❌ Use: !vs 2.5")

    # comandos manuais
    if message.content == "!ranking":
        await enviar_ranking()

    if message.content == "!meta":
        await verificar_meta()


# =========================================
# 🚀 START
# =========================================
@client.event
async def on_ready():
    print(f'🔥 Logado como {client.user}')
    client.loop.create_task(rotina_svs())

client.run(TOKEN)
