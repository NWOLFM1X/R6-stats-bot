from asyncio import tasks

import discord
from discord.ext import commands
import bs4
import json

with open("jsons/init.json")as f:
    config = json.load(f)
    prefix = config.get("prefix")
    TOKEN = config.get("token")

try:
    with open("jsons/users.json")as f:
        linked_users = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    linked_users = {}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    print(f"Logget ind som {bot.user}")

@bot.command("link")
async def link(ctx, username: str):
    user_id = str(ctx.author.id)

    if ctx.author.name in linked_users:
        await ctx.send(f"❌ Din Ubisoft-konto **{username}** er allerede linket til din Discord-bruger")
        return

    linked_users[ctx.author.name] = {
        "discord_id": str(user_id),
        "ubiName": username
    }

    with open("jsons/users.json", "w") as f:
        json.dump(linked_users, f, indent=4)
    await ctx.send(f"✅ Din Ubisoft-konto **{username}** er nu linket til din Discord-bruger.")

bot.run(TOKEN)