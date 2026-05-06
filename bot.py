import os
import discord
import requests
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# =======================
# VS (NÃO ALTERADO)
# =======================
@bot.command()
async def vs(ctx, valor: float):
    try:
        payload = {
            "usuario": ctx.author.display_name,
            "discord_id": str(ctx.author.id),
            "valor": valor
        }

        response = requests.post(f"{API_URL}/vs", json=payload)

        if response.status_code == 200:
            await ctx.send(f"🔥 VS registrado para {ctx.author.display_name}: {valor}")
        else:
            await ctx.send("❌ Erro ao salvar VS")

    except Exception as e:
        await ctx.send("❌ Erro ao registrar VS")
        print(e)


# =======================
# RANKING VS
# =======================
@bot.command()
async def ranking(ctx):
    try:
        response = requests.get(f"{API_URL}/ranking")
        data = response.json()

        if not data:
            await ctx.send("Sem dados.")
            return

        msg = "🏆 Ranking VS:\n"

        for i, player in enumerate(data, start=1):
            msg += f"{i}. {player['usuario']} - {float(player['total']):,.2f}\n"

        await ctx.send(msg)

    except Exception as e:
        await ctx.send("Erro ao buscar ranking")
        print(e)


# =======================
# F1 (AJUSTADO)
# =======================
@bot.command()
async def f1(ctx, valor: str):
    try:
        valor = valor.upper().replace(",", ".")

        multiplicador = 1

        if valor.endswith("K"):
            multiplicador = 1_000
            valor = valor[:-1]
        elif valor.endswith("M"):
            multiplicador = 1_000_000
            valor = valor[:-1]
        elif valor.endswith("B"):
            multiplicador = 1_000_000_000
            valor = valor[:-1]

        valor_final = float(valor) * multiplicador

        payload = {
            "usuario": ctx.author.display_name,
            "discord_id": str(ctx.author.id),
            "valor": valor_final
        }

        response = requests.post(f"{API_URL}/f1", json=payload)

        if response.status_code == 200:
            await ctx.send(
                f"🏁 F1 registrado para {ctx.author.display_name}: {valor_final:,.2f}"
            )
        else:
            await ctx.send("❌ Erro ao salvar F1")

    except:
        await ctx.send("❌ Valor inválido! Ex: 2.5M, 1.2B, 500K")


# =======================
# RANKING F1
# =======================
@bot.command()
async def rankingf1(ctx):
    try:
        response = requests.get(f"{API_URL}/ranking-f1")
        data = response.json()

        if not data:
            await ctx.send("Sem dados F1.")
            return

        msg = "🏎️ Ranking F1:\n"

        for i, player in enumerate(data, start=1):
            msg += f"{i}. {player['usuario']} - {float(player['total']):,.2f}\n"

        await ctx.send(msg)

    except Exception as e:
        await ctx.send("Erro ao buscar ranking F1")
        print(e)


bot.run(TOKEN)
