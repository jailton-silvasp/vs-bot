import os
import discord
import requests
from discord.ext import commands

# ================================
# 🔥 CONFIG
# ================================
TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = os.getenv("API_URL")

if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN não definido!")

if not API_URL:
    raise ValueError("❌ API_URL não definida!")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================================
# 🔥 EVENTO ONLINE
# ================================
@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")

# ================================
# 🔥 COMANDO VS (DIÁRIO)
# ================================
@bot.command()
async def vs(ctx, pontos: int):
    try:
        payload = {
            "player_name": ctx.author.display_name,
            "points": pontos
        }

        response = requests.post(f"{API_URL}/vs", json=payload)

        if response.status_code == 200:
            await ctx.send(f"🔥 VS registrado: {pontos}")
        else:
            await ctx.send("❌ Erro ao salvar VS")

    except Exception as e:
        await ctx.send("❌ Erro ao registrar VS")
        print("Erro VS:", e)

# ================================
# 🔥 COMANDO RANKING
# ================================
@bot.command()
async def ranking(ctx):
    try:
        response = requests.get(f"{API_URL}/ranking")

        if response.status_code != 200:
            await ctx.send("❌ API não respondeu")
            return

        data = response.json()

        if not data:
            await ctx.send("⚠️ Sem dados hoje.")
            return

        msg = "🏆 **Ranking do Dia** 🏆\n\n"

        for i, player in enumerate(data, start=1):
            nome = player.get("player_name", "Desconhecido")
            pontos = player.get("points", 0)

            msg += f"{i}. {nome} - {pontos}\n"

        await ctx.send(msg)

    except Exception as e:
        await ctx.send("❌ Erro ao buscar ranking")
        print("Erro Ranking:", e)

# ================================
# 🔥 COMANDO F1 (SEMANAL)
# ================================
@bot.command()
async def f1(ctx, pontos: int):
    try:
        payload = {
            "player_name": ctx.author.display_name,
            "points": pontos
        }

        response = requests.post(f"{API_URL}/f1", json=payload)

        if response.status_code == 200:
            await ctx.send(f"🏎️ F1 registrado: {pontos}")
        else:
            await ctx.send("❌ Erro ao salvar F1")

    except Exception as e:
        await ctx.send("❌ Erro ao registrar F1")
        print("Erro F1:", e)

# ================================
# 🔥 START BOT
# ================================
bot.run(TOKEN)
