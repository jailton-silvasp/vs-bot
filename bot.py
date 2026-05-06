import os
import discord
import requests
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# 🔥 VS
# =========================
@bot.command()
async def vs(ctx, pontos: float):
    try:
        payload = {
            "player_name": ctx.author.display_name,
            "discord_id": str(ctx.author.id),
            "points": pontos
        }

        response = requests.post(f"{API_URL}/vs", json=payload)

        if response.status_code == 200:
            await ctx.send(f"🔥 VS registrado para [{ctx.author.display_name}] : {pontos}")
        else:
            await ctx.send("❌ Erro ao salvar VS")
            print(response.text)

    except Exception as e:
        await ctx.send("❌ Erro ao salvar VS")
        print(e)

# =========================
# 🏎️ F1
# =========================
@bot.command()
async def f1(ctx, pontos: float):
    try:
        payload = {
            "player_name": ctx.author.display_name,
            "discord_id": str(ctx.author.id),
            "points": pontos
        }

        response = requests.post(f"{API_URL}/f1", json=payload)

        if response.status_code == 200:
            await ctx.send(f"🏎️ F1 registrado para [{ctx.author.display_name}] : {pontos}")
        else:
            await ctx.send("❌ Erro ao salvar F1")
            print(response.text)

    except Exception as e:
        await ctx.send("❌ Erro ao salvar F1")
        print(e)

# =========================
# 🏆 RANKING
# =========================
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
            msg += f"{i}. {player['usuario']} - {player['points']}\n"

        await ctx.send(msg)

    except Exception as e:
        await ctx.send("Erro ao buscar ranking")
        print(e)

# =========================
# 🚀 START
# =========================
bot.run(TOKEN)
