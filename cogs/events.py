import json

import discord
from discord.ext import commands
import datetime
from datetime import datetime

from main import linked_users, save_links



class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            cmd = ctx.message.content.split()[0]
            await ctx.send(f"**{cmd}** Eksisterer ikke.")
        elif isinstance(error, commands.NotOwner):
            await ctx.send("❌ Du har ikke tilladelser til at bruge denne kommando.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Du har ikke de nødvendige tilladelser til at bruge denne kommando.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Forkert argument. Tjek kommandoens syntax og prøv igen.")
        else:
            raise error

async def setup(bot):
    await bot.add_cog(Events(bot))
