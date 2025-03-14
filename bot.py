import discord
from discord.ext import commands
import os
import threading
from flask import Flask


TOKEN = os.getenv("DISCORD_TOKEN")  
WELCOME_CHANNEL_ID = 1282123711624773735  
TICKET_CATEGORY_ID = 1349849328335851540  
SUPPORT_CHANNEL_ID = 1337438563595190416  


app = Flask(__name__)

@app.route('/')
def home():
    return "Il bot è attivo!"

def run_flask():
    app.run(host="0.0.0.0", port=8000)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()


intents = discord.Intents.default()
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"welcome {member.mention}")


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="General", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)


        existing_channel = discord.utils.get(guild.channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"Hai già un ticket aperto: {existing_channel.mention}", ephemeral=True)
            return


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

        await ticket_channel.send(f"{user.mention}, grazie per aver aperto ticket saxz1n sarà subito da te\nUsa `!close` per chiudere il ticket.")
        await interaction.response.send_message(f"Ticket aperto: {ticket_channel.mention}", ephemeral=True)


@bot.command()
async def setup_ticket(ctx):
    embed = discord.Embed(title="Ticket", description="To create a ticket use the button below", color=discord.Color.blue())
    view = TicketView()
    await ctx.send(embed=embed, view=view)


@bot.command()
async def close(ctx):
    if ctx.channel.category_id == TICKET_CATEGORY_ID:
        await ctx.channel.delete()
    else:
        await ctx.send(" Non puoi chiudere questo canale!")


@bot.command()
async def ads(ctx, *, message: str = None):
    if not message and not ctx.message.attachments:
        await ctx.send("❌ Devi fornire un messaggio o allegare un'immagine!")
        return

    embed = discord.Embed(
        title="📢 Annuncio",
        description=message if message else " ",
        color=discord.Color.green()
    )

    if ctx.message.attachments:
        image_url = ctx.message.attachments[0].url
        embed.set_image(url=image_url)

    await ctx.send(embed=embed)

bot.run(TOKEN)
