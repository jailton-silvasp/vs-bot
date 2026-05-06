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
        elif valor.endswith("B") or valor.endswith("G"):
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
        await ctx.send("❌ Valor inválido! Ex: 2.5M, 1.2B, 500K, 2.8G")
