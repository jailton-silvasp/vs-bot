import os
import discord
import requests
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔥 FORMATADOR (PADRÃO G/M/K)
def formatar_valor(valor):
    if valor >= 1_000_000_000:
        return f"{valor / 1_000_000_000:.2f}G"
    elif valor >= 1_000_000:
        return f"{valor / 1_000_000:.2f}M"
    elif valor >= 1_000:
        return f"{valor / 1_000:.2f}K"
    else:
        return f"{valor:.2f}"

# 🔥 PARSER (entrada do usuário)
def parse_valor(valor):
    valor = valor.upper().replace(",", ".")
    multiplicador = 1

    if valor.endswith("K"):
        multiplicador = 1_000
        valor = valor[:-1]
    elif valor.endswith("M"):
        multiplicador = 1_000_000
        valor = valor[:-1]
    elif valor.endswith("B") or valor.endswith("G"):
        multiplicador = 1_000_000_000
        valor = valor[:-1]

    return float(valor) * multiplicador

# 🔥 VS
@bot.command()
async def vs(ctx, valor: str):
    try:
        valor_final = parse_valor(valor)

        payload = {
            "usuario": ctx.author.display_name,
            "discord_id": str(ctx.author.id),
            "valor": valor_final
        }

        response = requests.post(f"{API_URL}/vs", json=payload)

        if response.status_code == 200:
            await ctx.send(
                f"🔥 VS registrado para {ctx.author.display_name}: {formatar_valor(valor_final)}"
            )
        else:
            await ctx.send("❌ Erro ao salvar VS")

    except:
        await ctx.send("❌ Valor inválido! Ex: 2.5M, 1.2B, 2.8G")

# 🔥 F1
@bot.command()
async def f1(ctx, valor: str):
    try:
        valor_final = parse_valor(valor)

        payload = {
            "usuario": ctx.author.display_name,
            "discord_id": str(ctx.author.id),
            "valor": valor_final
        }

        response = requests.post(f"{API_URL}/f1", json=payload)

        if response.status_code == 200:
            await ctx.send(
                f"🏁 F1 registrado para {ctx.author.display_name}: {formatar_valor(valor_final)}"
            )
        else:
            await ctx.send("❌ Erro ao salvar F1")

    except:
        await ctx.send("❌ Valor inválido! Ex: 2.5M, 1.2B, 2.8G")

# 🔥 RANKING
@bot.command()
async def ranking(ctx):
    try:
        response = requests.get(f"{API_URL}/ranking")
        data = response.json()

        if not data:
            await ctx.send("Sem dados hoje.")
            return

        msg = "🏆 Ranking do Dia:\n"

        for i, player in enumerate(data, start=1):
            msg += f"{i}. {player['usuario']} - {formatar_valor(float(player['total']))}\n"

        await ctx.send(msg)

    except Exception as e:
        await ctx.send("❌ Erro ao buscar ranking")
        print(e)

bot.run(TOKEN)
