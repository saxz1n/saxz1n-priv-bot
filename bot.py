import discord
from discord.ext import commands
import os
import threading
from flask import Flask

# Variabili di configurazione
TOKEN = os.getenv("DISCORD_TOKEN")  # Usa variabile d'ambiente per sicurezza
WELCOME_CHANNEL_ID = 1282123711624773735  # Canale di benvenuto
TICKET_CATEGORY_ID = 1349849328335851540  # Categoria per i ticket
SUPPORT_CHANNEL_ID = 1337438563595190416  # Canale per il messaggio di apertura ticket

# Avvia Flask per tenere attivo il bot
app = Flask(__name__)

@app.route('/')
def home():
    return "Il bot è attivo!"

def run_flask():
    app.run(host="0.0.0.0", port=8000)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Configura il bot
intents = discord.Intents.default()
intents.members = True  # Necessario per il messaggio di benvenuto
bot = commands.Bot(command_prefix="!", intents=intents)

# Evento per il messaggio di benvenuto
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"👋 Benvenuto {member.mention} nel server!")

# Classe per gestire il pulsante di apertura ticket
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Apri un Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)

        # Controlla se l'utente ha già un ticket aperto
        existing_channel = discord.utils.get(guild.channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"Hai già un ticket aperto: {existing_channel.mention}", ephemeral=True)
            return

        # Permessi per il ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        # Creazione del canale
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{user.name.lower()}",
            category=category,
            overwrites=overwrites
        )

        await ticket_channel.send(f"👋 Ciao {user.mention}, il team di supporto ti risponderà al più presto!\nUsa `!close` per chiudere il ticket.")
        await interaction.response.send_message(f"✅ Ticket aperto: {ticket_channel.mention}", ephemeral=True)

# Comando per inviare il messaggio con il pulsante di apertura ticket
@bot.command()
async def setup_ticket(ctx):
    embed = discord.Embed(title="🎟️ Sistema Ticket", description="Clicca sul pulsante qui sotto per aprire un ticket di supporto.", color=discord.Color.blue())
    view = TicketView()
    await ctx.send(embed=embed, view=view)

# Comando per chiudere il ticket
@bot.command()
async def close(ctx):
    if ctx.channel.category_id == TICKET_CATEGORY_ID:
        await ctx.channel.delete()
    else:
        await ctx.send("❌ Non puoi chiudere questo canale!")

bot.run(TOKEN)
