print("🔥 BOT INICIANDO COM ROTINA SVS 🔥")

import discord
from discord.ext import commands, tasks
import requests
import os
import re
from datetime import datetime, timedelta
import pytz

TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")

CANAL_INFORMATIVO = 1500181167583006720

tz = pytz.timezone("America/Sao_Paulo")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------------
# AVATAR (NOVO - MÍNIMO)
# ------------------------
def get_avatar_url(user):
    try:
        if user.avatar:
            return user.avatar.url
        return user.default_avatar.url
    except:
        return None


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

    # sem sufixo = M
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

    avatar_url = get_avatar_url(ctx.author)

    agora = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)

    # 🔥 REGRA NOVA: após 23h conta como próximo dia
    if agora.hour >= 23:
        data = (agora + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        data = agora.strftime("%Y-%m-%d")

    payload = {
        "usuario": ctx.author.display_name,
        "discord_id": str(ctx.author.id),
        "valor": numero,
        "avatar_url": avatar_url,
        "data": data  # ✅ NOVO
    }

    try:
        requests.post(f"{API_URL}/vs", json=payload)

        await ctx.send(
            f"🔥 VS registrado para 『{ctx.author.display_name}』: {formatar_valor(numero)}"
        )

    except Exception as e:
        await ctx.send(f"❌ Erro ao registrar VS: {e}")


# ------------------------
# F1 (AJUSTADO CORRETAMENTE)
# ------------------------
@bot.command()
async def f1(ctx, valor: str):
    numero = converter_valor(valor)

    if numero is None:
        await ctx.send("❌ Valor inválido! Ex: 2.5M, 1.2G, 500K")
        return

    avatar_url = get_avatar_url(ctx.author)

    agora = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)
    data = agora.strftime("%Y-%m-%d")
    semana = agora.isocalendar()[1]

    payload = {
        "usuario": ctx.author.display_name,
        "discord_id": str(ctx.author.id),
        "valor": numero,
        "avatar_url": avatar_url,
        "data": data,          # ✅ NOVO
        "semana": semana       # ✅ NOVO
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

        for i, user in enumerate(data, start=1):

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
# ROTINA SVS (DIÁRIA) - INTACTA
# ------------------------
from datetime import datetime
from discord.ext import tasks

@tasks.loop(minutes=1)
async def rotina_svs():
    agora = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)

    if agora.hour == 23 and agora.minute == 0:
        canal = bot.get_channel(CANAL_INFORMATIVO)

        if not canal:
            return

        # AJUSTE AQUI: pega o próximo dia
        dia = (agora.weekday() + 1) % 7

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
🧩 Fragmentos de herói (azul, roxo e laranja)
🔋 Núcleos de Energia
📜 Medalhas (Sabedoria e Honra)
🏗️ Melhorias de edifícios
🔬 Pesquisa tecnológica
🎖️ Treinamento e promoção de soldados
📐 Plantas de design / Planta DX
⚙️ Engrenagens e Ligas de Titânio
🛡️ Equipamentos exclusivos / Equipamento vermelho D6
🎯 Precisão para construção
📦 Baús de chips laranja
🍖 Rações Táticas Avançadas
🧪 Poções Nutritivas
💡 Chips de Potencial
📘 Regulamentos de Treinamento (Comum e Avançado)

🚀 Use tudo acumulado e maximize sua pontuação!
""",

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
# START (INTACTO)
# ------------------------
import asyncio

async def start_bot():
    while True:
        try:
            print("🚀 Iniciando bot...")
            await bot.start(TOKEN)
        except Exception as e:
            print(f"❌ Erro crítico: {e}")
            print("⏳ Aguardando 60 segundos...")
            await asyncio.sleep(60)

asyncio.run(start_bot())
