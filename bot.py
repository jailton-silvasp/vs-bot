import discord
from discord.ext import commands
import requests
import os
import re

TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = os.getenv("API_URL")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------------
# FUNÇÃO CONVERSÃO
# ------------------------
def converter_valor(valor_str):
    valor_str = valor_str.upper().replace(",", ".")
    match = re.match(r"^(\d+(\.\d+)?)([KMB]?)$", valor_str)

    if not match:
        return None

    numero = float(match.group(1))
    sufixo = match.group(3)

    if sufixo == "K":
        numero *= 1_000
    elif sufixo == "M":
        numero *= 1_000_000
    elif sufixo == "B":
        numero *= 1_000_000_000

    return numero

# ------------------------
# FUNÇÃO FORMATAÇÃO
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
# COMANDO F1
# ------------------------
@bot.command()
async def f1(ctx, valor: str):
    numero = converter_valor(valor)

    if numero is None:
        await ctx.send("❌ Valor inválido! Ex: 2.5M, 1.2G, 500K")
        return

    payload = {
        "usuario": ctx.author.name,
        "discord_id": str(ctx.author.id),
        "valor": numero
    }

    try:
        requests.post(f"{API_URL}/f1", json=payload)

        valor_formatado = formatar_valor(numero)

        await ctx.send(
            f"🏁 F1 registrado para 『{ctx.author.name}』: {valor_formatado}"
        )

    except Exception as e:
        await ctx.send(f"❌ Erro ao registrar: {e}")

# ------------------------
# INICIAR BOT
# ------------------------
bot.run(TOKEN)
