import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True  # Necessario per il messaggio di benvenuto

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("MTM0OTg0OTAyNDUzMzg4OTAyNA.GuHXE6.iHZvBerZOf1KusZP_psYqq9EcJmNQvECmRfTMQ")  # Assicura che il token venga preso dall'ambiente

WELCOME_CHANNEL_ID = 1282123711624773735  # Sostituisci con l'ID del tuo canale di benvenuto
TICKET_CATEGORY_ID = 1349849328335851540  # Sostituisci con l'ID della categoria dove creare i ticket
SUPPORT_CHANNEL_ID = 1337438563595190416  # Sostituisci con l'ID del canale dove inviare il messaggio con il pulsante

# Lista per tenere traccia dei ticket aperti
open_tickets = {}

# Messaggio di benvenuto quando un utente entra nel server
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"welcome {member.mention} ")

# Comando per inviare il messaggio con il pulsante per creare il ticket
@bot.command()
async def setup_ticket(ctx):
    embed = discord.Embed(title="🎟️ Sistema Ticket", description="Clicca sul pulsante qui sotto per aprire un ticket di supporto.", color=discord.Color.blue())
    button = discord.ui.Button(label="🎫 Generale", style=discord.ButtonStyle.primary, custom_id="open_ticket")

    view = discord.ui.View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

# Evento per il click sul pulsante "Generale"
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"] == "open_ticket":
        guild = interaction.guild
        user = interaction.user
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)

        # Controlla se l'utente ha già un ticket aperto
        existing_channel = discord.utils.get(guild.channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"Hai già un ticket aperto: {existing_channel.mention}", ephemeral=True)
            return

        # Creazione del canale con permessi personalizzati
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{user.name.lower()}",
            category=category,
            overwrites=overwrites
        )

        await ticket_channel.send(f"👋 Ciao {user.mention}, il team di supporto ti risponderà al più presto!\nUsa `/close` per chiudere il ticket.")
        await interaction.response.send_message(f"✅ Ticket aperto: {ticket_channel.mention}", ephemeral=True)

# Comando per chiudere il ticket (solo per chi ha accesso al canale)
@bot.command()
async def close(ctx):
    if ctx.channel.category_id == TICKET_CATEGORY_ID:
        await ctx.channel.delete()
    else:
        await ctx.send("❌ Non puoi chiudere questo canale!")

bot.run(os.getenv("DISCORD_TOKEN"))  # Usa la variabile d'ambiente per la sicurezza
