print("🔥 BOT INICIANDO VERSÃO FINAL 🔥")

import discord
from discord.ext import commands
import requests
import os
import re

TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------------
# CONVERSÃO (K, M, G)
# ------------------------
def converter_valor(valor_str):
    valor_str = valor_str.upper().replace(",", ".")
    match = re.match(r"^(\d+(\.\d+)?)([KMG]?)$", valor_str)

    if not match:
        return None

    numero = float(match.group(1))
    sufixo = match.group(3)

    if sufixo == "K":
        numero *= 1_000
    elif sufixo == "M":
        numero *= 1_000_000
    elif sufixo == "G":
        numero *= 1_000_000_000

    return numero

# ------------------------
# FORMATAÇÃO (K, M, G)
# ------------------------
def formatar_valor(valor):
    if valor >= 1_000_000_000:
        return f"{valor/1_000_000_000:.2f}G"
    elif valor >= 1_000_000:
        return f"{valor/1_000_000:.2f}M"
    elif valor >= 1_000:
        return f"{valor/1_000:.2f}K"
    else:
        return f"{valor:.2f}"

# ------------------------
# TESTE DE API
# ------------------------
@bot.command()
async def pingapi(ctx):
    try:
        r = requests.get(API_URL)
        await ctx.send(f"✅ API ONLINE ({r.status_code})")
    except:
        await ctx.send("❌ API OFFLINE")

# ------------------------
# COMANDO VS
# ------------------------
@bot.command()
async def vs(ctx, valor: str):
    numero = converter_valor(valor)

    if numero is None:
        await ctx.send("❌ Valor inválido! Ex: 10, 2.5M, 1.2G, 500K")
        return

    payload = {
        "usuario": ctx.author.display_name,
        "discord_id": str(ctx.author.id),
        "valor": numero
    }

    try:
        r = requests.post(f"{API_URL}/vs", json=payload)

        if r.status_code != 200:
            await ctx.send("❌ Erro ao salvar VS")
            print(r.text)
            return

        valor_formatado = formatar_valor(numero)

        await ctx.send(
            f"🔥 VS registrado para 『{ctx.author.display_name}』: {valor_formatado}"
        )

    except Exception as e:
        await ctx.send(f"❌ Erro: {e}")

# ------------------------
# COMANDO F1
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
        "valor": numero
    }

    try:
        r = requests.post(f"{API_URL}/f1", json=payload)

        if r.status_code != 200:
            await ctx.send("❌ Erro ao salvar F1")
            print(r.text)
            return

        valor_formatado = formatar_valor(numero)

        await ctx.send(
            f"🏁 F1 registrado para 『{ctx.author.display_name}』: {valor_formatado}"
        )

    except Exception as e:
        await ctx.send(f"❌ Erro: {e}")

# ------------------------
# COMANDO RANKING
# ------------------------
@bot.command()
async def ranking(ctx):
    try:
        r = requests.get(f"{API_URL}/ranking")

        if r.status_code != 200:
            await ctx.send("❌ Erro ao buscar ranking")
            print(r.text)
            return

        data = r.json()

        if not data:
            await ctx.send("📭 Nenhum registro encontrado.")
            return

        mensagem = "🏆 **RANKING TOP 10**\n\n"

        for i, player in enumerate(data[:10], start=1):
            nome = player["usuario"]
            valor = formatar_valor(float(player["valor"]))

            mensagem += f"{i}. {nome} — {valor}\n"

        await ctx.send(mensagem)

    except Exception as e:
        await ctx.send(f"❌ Erro ao buscar ranking: {e}")

# ------------------------
# START
# ------------------------
bot.run(TOKEN)
