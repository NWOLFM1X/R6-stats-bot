import discord
from discord.ext import commands

import apiClass
import main
import json
import datetime
from datetime import datetime
import requests

# === Rank-navne ===
RANK_NAMES = [
    "Copper", "Bronze", "Silver", "Gold", "Platinum", "Emerald", "Diamond", "Champion"
]

try:
    with open("jsons/users.json") as f:
        linked_users = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    linked_users = {}


def save_links():
    with open("jsons/users.json", "w") as f:
        json.dump(linked_users, f, indent=4)


with open("jsons/init.json") as f:
    data = json.load(f)
    apiKey = data.get("api-key")

Ejerid = 1416884702370988052


# Delay mellem batches

class Comms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Loader extensions commands.py/events.py
    @commands.command()
    @commands.check(commands.is_owner())
    async def load(self, ctx):
        await main.load()
        await ctx.send("All cogs have been loaded.")

    # Kører opdaterings loopet
    @commands.command(name="reload")
    @commands.check_any(commands.is_owner())
    async def reload(self, ctx):
        print("🔄 Genindlæser botten...")
        await main.update_roles()
        print("✅ Bot genindlæst!")
        await ctx.send("✅ Bot genindlæst!")

    # En admin command hvor admins af discord serveren ka fjerne folks link til botten hvis de snyder sig til højere rank end de er f.eks ved at linke sig til en pro spiller
    @commands.command("remove")
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
    async def remove(self, ctx: commands.Context, member: discord.Member):
        if member.bot:
            await ctx.send("❌ Du kan ikke fjerne roller fra bots.")
            return

        user_name = member.name
        global linked_users  # hvis linked_users er defineret globalt
        if user_name in linked_users:
            removed = linked_users.pop(user_name)
            save_links()
            await ctx.send(f"🗑️ Fjernede link til **{removed['ubiName']}**.")
            print(f"🔗 {user_name} har fået sit link fjernet af {ctx.author.name}.")

            with open("linklogs.txt", "a") as log_file:
                log_file.write(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {ctx.author.name} har fjernet link til {removed['ubiName']} | Discord ID: {member.id}\n")

            # Fjern rank-roller hvis de findes
            current_roles = [r for r in member.roles if r.name in RANK_NAMES]
            if current_roles:
                try:
                    await member.remove_roles(*current_roles)
                    print(f"🔄 Fjernede roller fra {member.display_name}")
                except discord.Forbidden:
                    await ctx.send("⚠️ Botten har ikke tilladelser til at fjerne roller fra dette medlem.")
        else:
            await ctx.send("⚠️ Denne bruger har ikke en linket account.")

    # Bruges af folk til at sende fejl rapport til bottens ejer f.eks "botten opdatere ikke korrekt"
    @commands.command("bugreport")
    async def bugreport(self, ctx, *, besked: str):
        owner = await self.bot.fetch_user(self.bot.owner_id)

        embed = discord.Embed(
            title="⚠️ Bug Report!",
            description=besked,
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1088851944572993596/1365749929422618664/bad9c68f-d5a5-4b24-9fdc-4aaf73b39b58.png?ex=680e713d&is=680d1fbd&hm=3eafcb16ea8681ce53b7905f774331a978fbe969a887125244c9af33bea425db&")
        embed.set_footer(text=f"Reportet af {ctx.author} (id: {ctx.author.id})")

        try:
            await owner.send(embed=embed)
            await ctx.send("✅ Din bug report er blevet sendt! Tak fordi du hjælper med at forbedre botten.")
        except discord.Forbidden:
            await ctx.send("❌ Der var en fejl med at sende din bug report.. prøv igen senere!")

    # Sender en persons ingame stats når du skriver !stats <ubinavn>
    @commands.command("stats")
    async def stats(self, ctx, player: str):
        lookup_url = f"https://r6.statsapi.net/profiles/lookup?displayName={player}&platform=uplay"
        lookup_res = requests.get(url=lookup_url, headers=main.r6.apiHeaders)

        lookup_data = lookup_res.json()
        hsrate = str(lookup_data.get("headshotRate"))
        rank = r6.fetch_rank(player)
        get_image = f"https://static.stats.cc/siege/ranks/{rank}-small.webp"
        level = lookup_data.get("level")
        displayName = lookup_data.get("displayName")
        kd = r6.kdRatio(player)

        HSrate = hsrate.split(".")[0].capitalize()

        embedVar = discord.Embed(title=f"{displayName}", color=discord.Color.red())
        embedVar.add_field(name=f"{displayName}'s rank er {rank}", value=f"", inline=True)
        embedVar.add_field(name=f"Headshot rate: {HSrate}%", value=f"", inline=False)
        embedVar.add_field(name=f"KD: {kd}", value=f"", inline=False)
        embedVar.add_field(name=f"Account level: {level}", value=f"", inline=False)
        embedVar.set_thumbnail(url=get_image)
        await ctx.send(embed=embedVar)

    # Bottens hjælp command
    @commands.command("r6help")
    async def r6_help(self, ctx):
        embedVar = discord.Embed(title="Bot hjælp", color=discord.Color.red())
        embedVar.add_field(name="!link <Din siege account>", value="Linker din siege account til botten så dine roller blir opdateret!", inline=True)
        embedVar.add_field(name="!unlink", value="Fjerner dit link til botten så dine roller ik blir opdateret!", inline=True)
        embedVar.add_field(name="!minrank", value="Sender din linkede account rank i chatten", inline=True)
        embedVar.add_field(name="!bugreport <Buggen der skal reporteres>", value="Sender en besked til ejeren af botten angående fejl (MÅ IKKE MISBRUGES!)", inline=False)
        embedVar.add_field(name="!stats <siege account>", value="Tjekker en spillers siege rank, bemærk den viser personens sæson max rank", inline=True)
        await ctx.send(embed=embedVar)

    # Commanden til at linke dig til botten, den gemmer i jsons/users.json, gemmer dit ubi navn discord navn og id
    @commands.command("link")
    async def link(self, ctx, username: str):
        user_name = ctx.author.name
        if user_name in linked_users:
            await ctx.send(f"⚠️ Du har allerede linket en konto.")
            return

        for user, data in linked_users.items():
            if data["ubiName"].lower() == username.lower():
                await ctx.send(f"⚠️ Kontoen **{username}** er allerede linket til en anden.")
                return

        if r6.fetch_profile(username) is None:
            await ctx.send(f"⚠️ Vi kan ikke finde nogen konto med navnet {username}.")
        else:
            linked_users[user_name] = {
                "discord_id": str(ctx.author.id),
                "ubiName": username
            }
            save_links()
            print(f"🔗 {user_name} har linket {username}.")
            with open("linklogs.txt", "a") as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {user_name} har linket {username} | Discord ID: {ctx.author.id}\n")

            await ctx.send(f"✅ Kontoen **{username}** er nu linket til din Discord.")
            await ctx.author.edit(nick=username)

    # Fjerner dit link til botten
    @commands.command("unlink")
    async def unlink(self, ctx):
        user_name = ctx.author.name
        if user_name in linked_users:
            removed = linked_users.pop(user_name)
            save_links()
            await ctx.send(f"🗑️ Fjernede link til **{removed['ubiName']}**.")
            print(f"🔗 {user_name} har fjernet sit link.")
            with open("linklogs.txt", "a") as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {user_name} har fjernet link til {removed['ubiName']} | Discord ID: {ctx.author.id}\n")
            # Fjern roller
            member = ctx.author
            current_roles = [r for r in member.roles if r.name in RANK_NAMES]
            if current_roles:
                try:
                    await member.remove_roles(*current_roles)
                    print(f"🔄 Fjernede roller fra {member.display_name}")
                except discord.Forbidden:
                    print(f"⚠️ Botten har ikke tilladelser til at fjerne roller fra {member.display_name}")
            await ctx.author.edit(nick=ctx.author.name)  # Gendan originalt navn
            print(f"🔄 Gendannede {member.display_name}'s originale navn.")
        else:
            await ctx.send("⚠️ Du har ikke linket nogen konto.")

    # Sender din egen rank i Rainbow six siege
    @commands.command("minrank")
    async def minrank(self, ctx):
        user_name = ctx.author.name
        if user_name in linked_users:

            lookup_url = f"https://r6.statsapi.net/profiles/lookup?displayName={linked_users[user_name]['ubiName']}&platform=uplay"

            lookup_res = requests.get(url=lookup_url, headers=main.r6.apiHeaders)

            lookup_data = lookup_res.json()

            rank = r6.fetch_rank(linked_users[user_name]["ubiName"])
            get_image = f"https://static.stats.cc/siege/ranks/{rank}-small.webp"
            displayName = lookup_data.get("displayName")

            embedVar = discord.Embed(title="Din rank", colour=discord.Colour.red())
            embedVar.add_field(name=f"{displayName}'s rank er {rank}", value=f"", inline=True)
            embedVar.set_thumbnail(url=get_image)
            await ctx.send(embed=embedVar)
        else:
            await ctx.send("⚠️ Du har ikke linket nogen konto.")


r6 = apiClass.r6api(apiKey)


async def setup(bot):
    await bot.add_cog(Comms(bot))