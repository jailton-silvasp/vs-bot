print("🔥 BOT INICIANDO COM ROTINA SVS 🔥")

import discord
from discord.ext import commands, tasks
import requests
import os
import re
from datetime import datetime
import pytz

TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")

# 👉 COLOQUE O ID DO CANAL "informativo"
CANAL_INFORMATIVO = 1500181167583006720

tz = pytz.timezone("America/Sao_Paulo")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------------
# CONVERSÃO
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
# FORMATAÇÃO
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
# NOME EXIBIÇÃO
# ------------------------
def get_nome(ctx):
    return ctx.author.display_name

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
        "usuario": get_nome(ctx),
        "discord_id": str(ctx.author.id),
        "valor": numero
    }

    try:
        requests.post(f"{API_URL}/f1", json=payload)

        await ctx.send(
            f"🏁 F1 registrado para 『{get_nome(ctx)}』: {formatar_valor(numero)}"
        )

    except Exception as e:
        await ctx.send(f"❌ Erro ao registrar: {e}")

# ------------------------
# COMANDO VS
# ------------------------
@bot.command()
async def vs(ctx, valor: str):
    numero = converter_valor(valor)

    if numero is None:
        await ctx.send("❌ Valor inválido! Ex: 10M, 2.5G")
        return

    payload = {
        "usuario": get_nome(ctx),
        "discord_id": str(ctx.author.id),
        "valor": numero
    }

    try:
        requests.post(f"{API_URL}/vs", json=payload)

        await ctx.send(
            f"🔥 VS registrado para 『{get_nome(ctx)}』: {formatar_valor(numero)}"
        )

    except Exception as e:
        await ctx.send(f"❌ Erro ao registrar: {e}")

# ------------------------
# RANKING (DIÁRIO)
# ------------------------
@bot.command()
async def ranking(ctx):
    try:
        r = requests.get(f"{API_URL}/ranking?period=day")

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
            member = ctx.guild.get_member(int(discord_id)) if discord_id else None

            if member:
                nome = member.display_name
            else:
                nome = user.get("usuario") or "Desconhecido"

            # 🔥 AQUI É A CORREÇÃO
            total = user.get("total")

            # 👉 NÃO CONVERTER MAIS
            msg += f"{i}. {nome} — {total}\n"

        await ctx.send(msg)

    except Exception as e:
        await ctx.send(f"❌ Erro ao buscar ranking: {e}")

# ------------------------
# ROTINA SVS (00:00)
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
            0: """📅 Dia 1 – Expansão do Abrigo
👾 Guardar: Radares, Equipamentos, Núcleos de Energia, Baús da Sorte...

🏗>> Construção
📜>> Medalhas da Sabedoria
🔬>> Pesquisa
⚙️>> Aceleradores
💰>> Coleta de Recursos""",

            1: """📅 Dia 2 – Iniciativa de Heróis
📡 Missões de Radar
🎖 Recrutamento Prime
🧩 Fragmentos de Herói
💡 Dica Pro: Treinar tropas antes do reset""",

            2: """📅 Dia 3 – Continue Progredindo
🚚 Caminhões nível S
🕶 Missões laranja
🪖 Treinamento
🔧 Equipamento Vermelho""",

            3: """📅 Dia 4 – Especialista em Armas
📡 Radar
💥 Rallys
🧟 Zumbis
⚙️ Aceleradores""",

            4: """📅 Dia 5 – Crescimento Holístico
🧩 Fragmentos
🔋 Núcleos
📜 Medalhas
💡 Use tudo acumulado""",

            5: """📅 Dia 6 – Destruidor de Inimigos
🚚 Caminhões S
🎯 PvP
💀 Perdas contam
💡 Use escudo se necessário""",

            6: """🔥 SVS ENCERRADO
💪 Dia de recuperação"""
        }

        await canal.send(f"@everyone\n\n{mensagens[dia]}")

# ------------------------
# READY
# ------------------------
@bot.event
async def on_ready():
    print(f"🤖 Logado como {bot.user}")
    rotina_svs.start()

# ------------------------
# START
# ------------------------
bot.run(TOKEN)
