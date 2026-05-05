import discord
from datetime import datetime
import os
import asyncio
import pytz
import requests

# ===== CONFIG =====
TOKEN = os.getenv("DISCORD_TOKEN")

CANAL_VS = int(os.getenv("CANAL_VS"))
CANAL_AVISOS = int(os.getenv("CANAL_AVISOS"))

API_URL = os.getenv("API_URL")  # EX: https://api-svs-production.up.railway.app

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

tz = pytz.timezone("America/Sao_Paulo")

# ===== CONTROLE =====
ultimo_envio = None
ultimo_ranking = None
ultimo_alerta = None


# =========================================
# 🏆 RANKING VIA API + EMBED
# =========================================
async def enviar_ranking():
    canal = client.get_channel(CANAL_AVISOS)

    if not canal:
        print("❌ Canal não encontrado")
        return

    try:
        res = requests.get(f"{API_URL}/ranking", timeout=5)
        data = res.json()
    except Exception as e:
        print("❌ Erro ao buscar ranking:", e)
        return

    embed = discord.Embed(
        title="🏆 Ranking SVS do Dia",
        color=0x00ff00
    )

    if data:
        for i, item in enumerate(data[:10], start=1):
            nome = item.get("usuario", "Desconhecido")
            total = float(item.get("total", 0))

            embed.add_field(
                name=f"{i}º {nome}",
                value=f"{round(total, 2)}M",
                inline=False
            )
    else:
        embed.description = "Sem registros hoje."

    await canal.send(embed=embed)


# =========================================
# ⚠️ META VIA API
# =========================================
async def verificar_meta():
    canal = client.get_channel(CANAL_AVISOS)

    if not canal:
        return

    try:
        res = requests.get(f"{API_URL}/ranking", timeout=5)
        data = res.json()
    except Exception as e:
        print("❌ Erro ao verificar meta:", e)
        return

    nao_bateram = [
        u.get("usuario", "Desconhecido")
        for u in data
        if float(u.get("total", 0)) < 2
    ]

    if nao_bateram:
        mensagem = "⚠️ **NÃO BATERAM 2M HOJE:**\n\n"
        for user in nao_bateram:
            mensagem += f"- {user}\n"

        await canal.send(mensagem)


# =========================================
# 🚀 ROTINA AUTOMÁTICA
# =========================================
async def rotina_svs():
    global ultimo_envio, ultimo_ranking, ultimo_alerta

    await client.wait_until_ready()

    while not client.is_closed():
        agora = datetime.now(tz)
        hoje = agora.strftime("%d/%m/%Y")

        canal = client.get_channel(CANAL_AVISOS)

        if canal:

            # 🔥 SVS 00:00
            if agora.hour == 0 and agora.minute == 0:
                if ultimo_envio != hoje:

                    dia = agora.weekday()

                    mensagens = {
                        0: f"📅 Dia 1 – Expansão ({hoje})\n🏗 Construção | 🔬 Pesquisa | 💰 Coleta",
                        1: f"📅 Dia 2 – Heróis ({hoje})\n📡 Radar | 🎖 Recrutamento",
                        2: f"📅 Dia 3 – Tropas ({hoje})\n🪖 Treino | 🚚 Missões",
                        3: f"📅 Dia 4 – Armas ({hoje})\n💥 Rally | 🧟 Zumbis",
                        4: f"📅 Dia 5 – Crescimento ({hoje})\n🧩 Fragmentos",
                        5: f"📅 Dia 6 – Guerra ({hoje})\n⚔️ PvP",
                        6: f"🔥 SVS ENCERRADO ({hoje})"
                    }

                    await canal.send(mensagens.get(dia))
                    ultimo_envio = hoje

            # 🏆 23:55 → ranking
            if agora.hour == 23 and agora.minute == 55:
                if ultimo_ranking != hoje:
                    print("⏰ Enviando ranking...")
                    await enviar_ranking()
                    ultimo_ranking = hoje

            # ⚠️ 23:57 → alerta
            if agora.hour == 23 and agora.minute == 57:
                if ultimo_alerta != hoje:
                    print("⏰ Verificando meta...")
                    await verificar_meta()
                    ultimo_alerta = hoje

        await asyncio.sleep(60)


# =========================================
# 🎮 COMANDOS
# =========================================
@client.event
async def on_message(message):
    if message.author.bot:
        return

    # 📌 REGISTRO VS
    if message.channel.id == CANAL_VS:

        if message.content.startswith("!vs"):
            try:
                valor = float(message.content.split(" ")[1])

                if valor <= 0:
                    await message.channel.send("❌ Valor inválido")
                    return

                # 🔥 NOME CORRIGIDO (ANTI-UNDEFINED)
                if message.guild:
                    usuario = message.author.display_name
                else:
                    usuario = message.author.name

                if not usuario or usuario == "undefined":
                    usuario = message.author.name

                print(f"👤 Usuario capturado: {usuario}")

                # 🔥 ENVIO API CORRETO
                try:
                    response = requests.post(
                        f"{API_URL}/vs",
                        json={
                            "user": usuario,
                            "vs": valor
                        },
                        timeout=10
                    )

                    print("📡 STATUS:", response.status_code)
                    print("📨 RESPOSTA:", response.text)

                    if response.status_code == 200:
                        await message.channel.send(f"✅ VS registrado: {valor}M")
                    else:
                        await message.channel.send("❌ API retornou erro")

                except Exception as e:
                    print("❌ ERRO REQUEST:", e)
                    await message.channel.send("❌ Erro ao conectar na API")

            except:
                await message.channel.send("❌ Use: !vs 2.5")

    # 📊 COMANDOS
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
