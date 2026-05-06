import os
import discord
import requests
from discord.ext import commands

# =============================
# 🔥 CONFIG
# =============================
TOKEN = os.getenv("TOKEN")  # 👈 conforme você usa
API_URL = os.getenv("API_URL")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =============================
# 🚀 EVENTO ONLINE
# =============================
@bot.event
async def on_ready():
    print(f"🔥 Bot online como {bot.user}")
    print(f"🌐 API URL: {API_URL}")

# =============================
# 🔥 COMANDO VS
# =============================
@bot.command()
async def vs(ctx, pontos: float):
    try:
        payload = {
            "player_name": ctx.author.display_name,  # 👈 nome exibido no Discord
            "discord_id": str(ctx.author.id),
            "points": pontos
        }

        response = requests.post(f"{API_URL}/vs", json=payload)

        if response.status_code == 200:
            await ctx.send(f"🔥 VS registrado para **{ctx.author.display_name}**: {pontos}")
        else:
            await ctx.send("❌ Erro ao salvar VS")
            print("ERRO API:", response.text)

    except Exception as e:
        await ctx.send("❌ Erro ao salvar VS")
        print("EXCEPTION VS:", e)

# =============================
# 🏎️ COMANDO F1
# =============================
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
            await ctx.send(f"🏎️ F1 registrado para **{ctx.author.display_name}**: {pontos}")
        else:
            await ctx.send("❌ Erro ao salvar F1")
            print("ERRO API:", response.text)

    except Exception as e:
        await ctx.send("❌ Erro ao salvar F1")
        print("EXCEPTION F1:", e)

# =============================
# 🏆 COMANDO RANKING
# =============================
@bot.command()
async def ranking(ctx):
    try:
        response = requests.get(f"{API_URL}/ranking")

        if response.status_code != 200:
            await ctx.send("❌ Erro ao buscar ranking")
            print("ERRO API:", response.text)
            return

        data = response.json()

        if not data:
            await ctx.send("📊 Nenhum registro hoje.")
            return

        msg = "🏆 **Ranking do Dia**\n\n"

        for i, player in enumerate(data, start=1):
            nome = player.get("usuario", "Desconhecido")  # 👈 vem do banco
            pontos = player.get("points", 0)

            msg += f"{i}. **{nome}** - {pontos}\n"

        await ctx.send(msg)

    except Exception as e:
        await ctx.send("❌ Erro ao buscar ranking")
        print("EXCEPTION RANKING:", e)

# =============================
# 🧪 DEBUG (VALIDAÇÃO API)
# =============================
@bot.command()
async def teste(ctx):
    try:
        response = requests.get(f"{API_URL}")

        if response.status_code == 200:
            await ctx.send("✅ API ONLINE")
        else:
            await ctx.send("❌ API respondeu com erro")

    except Exception as e:
        await ctx.send("❌ API não respondeu")
        print("EXCEPTION TESTE:", e)

# =============================
# 🚀 START BOT
# =============================
bot.run(TOKEN)
