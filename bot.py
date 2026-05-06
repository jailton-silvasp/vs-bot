import os
import discord
from discord.ext import commands
import requests
from datetime import datetime

TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= VS =================
@bot.command()
async def vs(ctx, valor: float):
    usuario = ctx.author.display_name
    discord_id = str(ctx.author.id)

    requests.post(f"{API_URL}/vs", json={
        "usuario": usuario,
        "discord_id": discord_id,
        "valor": valor
    })

    await ctx.send(f"🔥 {usuario} registrou {valor} VS")

# ================= F1 =================
@bot.command()
async def f1(ctx, valor: float):
    usuario = ctx.author.display_name
    discord_id = str(ctx.author.id)

    semana = datetime.now().strftime("%Y-%W")

    requests.post(f"{API_URL}/f1", json={
        "usuario": usuario,
        "discord_id": discord_id,
        "valor": valor,
        "semana": semana
    })

    await ctx.send(f"🏁 {usuario} registrou {valor} F1")

# ================= RANKING =================
@bot.command()
async def ranking(ctx):
    hoje = datetime.now().strftime("%Y-%m-%d")

    res = requests.get(f"{API_URL}/ranking?data={hoje}")
    data = res.json()

    msg = "🏆 Ranking VS:\n"
    for i, r in enumerate(data, 1):
        msg += f"{i}. {r['usuario']} - {r['total']}\n"

    await ctx.send(msg)

bot.run(TOKEN)
