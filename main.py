import asyncio
import json
import os

import discord
from discord.ext import commands, tasks
import datetime
from datetime import datetime

import apiClass

# === Konfiguration ===

with open("jsons/init.json") as f:
    config = json.load(f)
    prefix = config.get("prefix")
    TOKEN = config.get("token")
    KEY = config.get("api-key")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefix, intents=intents, owner_id=1416884702370988052, help_command=None)

# == rank navne
RANK_NAMES = [
    "Copper", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond", "Champion"
]

# === Load linked users ===
try:
    with open("jsons/users.json") as f:
        linked_users = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    linked_users = {}

def save_links():
    with open("jsons/users.json", "w") as f:
        json.dump(linked_users, f, indent=4)

# === Roller ===
# Funktionen der opdatere folks rank på discord hvis de er steget i rank i rainbow six siege
async def update_member_role(guild, member, rank):
    rank_tier = rank.split("-")[0].capitalize()  # Fjerner '-3' eller lignende fra ranken

    if rank_tier not in RANK_NAMES:
        print(f"❌ Ukendt rank: {rank_tier} for {member.display_name}")
        return

    role = discord.utils.get(guild.roles, name=rank_tier)
    if not role:
        role = await guild.create_role(name=rank_tier)

    # Find nuværende rank på Discord
    current_roles = [r.name for r in member.roles if r.name in RANK_NAMES]
    if current_roles:
        current_rank = current_roles[0]  # Antager at spiller kun har én rank
        current_rank_index = RANK_NAMES.index(current_rank)
        rank_index = RANK_NAMES.index(rank_tier)

        # Hvis den nuværende rank er lavere end den ønskede rank
        if current_rank_index < rank_index:
            # Fjern gamle roller, som ikke matcher den ønskede rank
            to_remove = [r for r in member.roles if r.name in RANK_NAMES and r.name != rank_tier]
            if to_remove:
                try:
                    await member.remove_roles(*to_remove)
                    print(f"🔄 Fjernede gamle roller fra {member.display_name}")
                except discord.Forbidden:
                    print(f"⚠️ Botten har ikke tilladelser til at fjerne roller fra {member.display_name}")
                    return

            # Tilføj den nye rolle
            try:
                await member.add_roles(role)
                print(f"🎖️ {member.display_name} fik rank: {rank_tier}")
            except discord.Forbidden:
                print(f"⚠️ Botten har ikke tilladelser til at tilføje rollen til {member.display_name}")
        elif current_rank_index == rank_index:
            print(f"ℹ️ {member.display_name} har allerede den korrekte rank: {rank_tier}")
        else:
            # Hvis Discord rank er højere end den ønskede rank, så fjern den gamle og tilføj den nye
            to_remove = [r for r in member.roles if r.name in RANK_NAMES and r.name != rank_tier]
            if to_remove:
                try:
                    await member.remove_roles(*to_remove)
                    print(f"🔄 Fjernede gamle roller fra {member.display_name}")
                except discord.Forbidden:
                    print(f"⚠️ Botten har ikke tilladelser til at fjerne roller fra {member.display_name}")
                    return

            # Tilføj den nye rolle
            try:
                await member.add_roles(role)
                print(f"🎖️ {member.display_name} fik rank: {rank_tier}")
            except discord.Forbidden:
                print(f"⚠️ Botten har ikke tilladelser til at tilføje rollen til {member.display_name}")
    else:
        # Hvis medlemmet ikke har nogen rank, tilføj den nye rolle
        try:
            await member.add_roles(role)
            print(f"🎖️ {member.display_name} fik rank: {rank_tier}")
        except discord.Forbidden:
            print(f"⚠️ Botten har ikke tilladelser til at tilføje rollen til {member.display_name}")

async def process_member(guild, member):
    username = linked_users.get(member.name, {}).get("ubiName")
    if not username:
        return

    rank = r6.fetch_rank(username)
    if rank and rank != "Ukendt":
        await update_member_role(guild, member, rank)
    else:
        print(f"⚠️ Kunne ikke finde rank for {username}")

# Printer nyttige ting i konsol når botten starter og ændrer dens status på discord
@bot.event
async def on_ready():
    print(f"✅ Logget ind som {bot.user}")
    print(f"👥 Antal servere: {len(bot.guilds)}")
    print(f"👤 Antal brugere: {len(set(bot.get_all_members()))}")
    await bot.change_presence(activity=discord.Game(name=f"{prefix}r6help | Opdaterer hver time!"))
    update_roles.start()

# Opdaterings loopet der kører 1 gang i timen som tjekker efter folk er steget i rank
@tasks.loop(minutes=60)
async def update_roles():
    print(f"🔁 Opdaterer roller... | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    members_to_update = []

    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot and member.name in linked_users:
                members_to_update.append((guild, member))

    batch_size = 20
    for i in range(0, len(members_to_update), batch_size):
        batch = members_to_update[i:i+batch_size]
        tasks_in_batch = []

        for guild, member in batch:
            tasks_in_batch.append(process_member(guild, member))

        await asyncio.gather(*tasks_in_batch)
        await asyncio.sleep(2)  # Delay mellem batches

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print("cogs loaded")

async def main():
    await load()
    await bot.start(TOKEN)

r6 = apiClass.r6api(KEY)

if __name__ == "__main__":
    asyncio.run(main())