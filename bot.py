print("🔥 BOT INICIANDO COM ROTINA SVS 🔥")

import asyncio
import discord
from discord.ext import commands, tasks
import requests
import os
import re
from datetime import datetime
import pytz

TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")

CANAL_INFORMATIVO = 1500181167583006720

tz = pytz.timezone("America/Sao_Paulo")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ------------------------
# COMUNICAÇÃO COM A API
# ------------------------

def registrar_na_api(endpoint, payload):
    if not API_URL:
        raise RuntimeError("A variável API_URL não está configurada.")

    response = requests.post(
        f"{API_URL.rstrip('/')}/{endpoint}",
        json=payload,
        timeout=(5, 20)
    )
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("A API retornou uma resposta inválida.") from exc

    if not isinstance(data, dict) or data.get("ok") is not True:
        raise RuntimeError("A API não confirmou o salvamento.")

    return True

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

    payload = {
        "usuario": ctx.author.display_name,
        "discord_id": str(ctx.author.id),
        "valor": numero
    }

    try:
        await asyncio.to_thread(registrar_na_api, "vs", payload)

        await ctx.send(
            f"🔥 VS registrado para 『{ctx.author.display_name}』: {formatar_valor(numero)}"
        )

    except Exception as e:
        print(f"❌ Falha ao registrar VS: {e}")
        await ctx.send(
            "⚠️ Não consegui confirmar o salvamento do VS. "
            "Confira o dashboard antes de tentar registrar novamente."
        )


# ------------------------
# F1
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
        await asyncio.to_thread(registrar_na_api, "f1", payload)

        await ctx.send(
            f"🏁 F1 registrado para 『{ctx.author.display_name}』: {formatar_valor(numero)}"
        )

    except Exception as e:
        print(f"❌ Falha ao registrar F1: {e}")
        await ctx.send(
            "⚠️ Não consegui confirmar o salvamento do F1. "
            "Confira o dashboard antes de tentar registrar novamente."
        )


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

        for i, user in enumerate(data[:10], start=1):

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
# ROTINA SVS (DIÁRIA)
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
# KEEP-ALIVE DA API / BANCO
# ------------------------
@tasks.loop(minutes=4)
async def manter_api_ativa():
    if not API_URL:
        print("⚠️ KEEP-ALIVE: API_URL não configurada.")
        return

    for tentativa in range(1, 4):
        try:
            response = await asyncio.to_thread(
                requests.get,
                f"{API_URL.rstrip('/')}/health",
                timeout=(5, 15)
            )
            response.raise_for_status()
            data = response.json()

            if data.get("ok") is True and data.get("database") == "connected":
                print("💚 KEEP-ALIVE: API e banco acessíveis.")
                return

            raise RuntimeError("Health check não confirmou conexão com o banco.")

        except Exception as e:
            print(f"⚠️ KEEP-ALIVE tentativa {tentativa}/3: {e}")
            if tentativa < 3:
                await asyncio.sleep(5 * tentativa)


# ------------------------
# READY
# ------------------------
@bot.event
async def on_ready():
    print(f"🤖 Logado como {bot.user}")

    if not rotina_svs.is_running():
        rotina_svs.start()

    if not manter_api_ativa.is_running():
        manter_api_ativa.start()


# ------------------------
# START
# ------------------------
bot.run(TOKEN)
