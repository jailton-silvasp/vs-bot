print("🔥 BOT INICIANDO COM ROTINA SVS 🔥")

import discord
from discord.ext import commands, tasks
import requests
import os
import re
from datetime import datetime
import pytz
import time

TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")

CANAL_INFORMATIVO = 1500181167583006720

tz = pytz.timezone("America/Sao_Paulo")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------------
# CONVERSÃO (K/M/G → número)
# ------------------------
def converter_valor(valor_str):
    valor_str = valor_str.upper().replace(",", ".")

    match = re.match(r"^(\d+(\.\d+)?)([KMG]?)$", valor_str)

    if not match:
        return None

    numero = float(match.group(1))
    sufixo = match.group(3)

    if sufixo == "":
        numero *= 1_000_000
    elif sufixo == "K":
        numero *= 1_000
    elif sufixo == "M":
        numero *= 1_000_000
    elif sufixo == "G":
        numero *= 1_000_000_000

    return numero


# ------------------------
# FORMATAÇÃO GLOBAL
# ------------------------
def formatar_valor(valor):
    try:
        valor = float(valor)
    except:
        return "0.00"

    if valor >= 1_000_000_000:
        return f"{valor/1_000_000_000:.2f}G"
    elif valor >= 1_000_000:
        return f"{valor/1_000_000:.2f}M"
    elif valor >= 1_000:
        return f"{valor/1_000:.2f}K"
    else:
        return f"{valor:.2f}"


# ------------------------
# VS
# ------------------------
@bot.command()
async def vs(ctx, valor: str):
    numero = converter_valor(valor)

    if numero is None:
        await ctx.send("❌ Valor inválido! Ex: 2.5M, 1.2G, 500K")
        return

    payload = {
        "usuario": ctx.author.display_name,
        "discord_id": str(ctx.author.id),
        "valor": numero,
        "avatar_url": str(ctx.author.display_avatar.url)
    }

    try:
        requests.post(f"{API_URL}/vs", json=payload)

        await ctx.send(
            f"🔥 VS registrado para 『{ctx.author.display_name}』: {formatar_valor(numero)}"
        )

    except Exception as e:
        await ctx.send(f"❌ Erro ao registrar VS: {e}")


# ------------------------
# F1
# ------------------------
@bot.command()
async def f1(ctx, valor: str):
    numero = converter_valor(valor)

    if numero is None:
        await ctx.send("❌ Valor inválido! Ex: 2.5M, 1.2G, 500K")
        return

    payload = {
        "usuario": ctx.author.display_name,
        "discord_id": str(ctx.author.id),
        "valor": numero,
        "avatar_url": str(ctx.author.display_avatar.url)
    }

    try:
        requests.post(f"{API_URL}/f1", json=payload)

        await ctx.send(
            f"🏁 F1 registrado para 『{ctx.author.display_name}』: {formatar_valor(numero)}"
        )

    except Exception as e:
        await ctx.send(f"❌ Erro ao registrar F1: {e}")


# ------------------------
# RANKING (DIÁRIO)
# ------------------------
@bot.command()
async def ranking(ctx):
    try:
        r = requests.get(f"{API_URL}/ranking?period=day", timeout=10)

        if r.status_code != 200:
            await ctx.send(f"❌ API erro: {r.status_code}")
            return

        data = r.json()

        if not data:
            await ctx.send("📉 Sem dados no ranking de hoje ainda.")
            return

        msg = "🏆 RANKING DO DIA (TOP 10)\n\n"

        for i, user in enumerate(data[:10], start=1):

            discord_id = user.get("discord_id")

            member = None
            try:
                member = ctx.guild.get_member(int(discord_id)) if discord_id else None
            except:
                member = None

            nome = member.display_name if member else user.get("usuario", "Desconhecido")

            try:
                total_num = float(user.get("total", 0))
            except:
                total_num = 0.0

            msg += f"{i}. {nome} — {formatar_valor(total_num)}\n"

        await ctx.send(msg)

    except Exception as e:
        await ctx.send(f"❌ Erro ao buscar ranking: {e}")
        print(e)


# ------------------------
# ROTINA SVS
# ------------------------
@tasks.loop(minutes=1)
async def rotina_svs():
    agora = datetime.now(tz)

    if agora.hour == 0 and agora.minute == 0:
        canal = bot.get_channel(CANAL_INFORMATIVO)

        if not canal:
            return

        dia = agora.weekday()

        mensagens = {
            0: "📅 Dia 1 – Expansão do Abrigo",
            1: "📅 Dia 2 – Iniciativa de Heróis",
            2: "📅 Dia 3 – Continue Progredindo",
            3: "📅 Dia 4 – Especialista em Armas",
            4: "📅 Dia 5 – Crescimento Holístico",
            5: "📅 Dia 6 – Destruidor de Inimigos",
            6: "🔥 SVS ENCERRADO"
        }

        await canal.send(f"@everyone\n\n{mensagens[dia]}")


# ------------------------
# READY
# ------------------------
@bot.event
async def on_ready():
    print(f"🤖 Logado como {bot.user}")
    if not rotina_svs.is_running():
        rotina_svs.start()


# ------------------------
# START (ANTI-RATE LIMIT)
# ------------------------
while True:
    try:
        print("🚀 Iniciando bot...")
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        print("⏳ Aguardando 60 segundos para evitar rate limit...")
        time.sleep(60)
