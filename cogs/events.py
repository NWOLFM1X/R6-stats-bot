
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
        else:
            raise error

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        user_name = member.name
        global linked_users

        if user_name in linked_users:
            removed = linked_users.pop(user_name)
            save_links()
            print(f"🚫 {user_name} er blevet bannet og linket er fjernet")

            with open("banlogs.txt", "a") as f:
                f.write(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
                    f"{user_name} blev bannet fra {guild.name}, link til {removed['ubiName']} fjernet | Discord ID: {member.id}\n"
                )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        user_name = member.name
        global linked_users

        if user_name in linked_users:
            removed = linked_users.pop(user_name)
            save_links()
            print(f"👋 Fjernede link til {removed['ubiName']} (forladt/kick: {user_name})")

            with open("banlogs.txt", "a") as log_file:
                log_file.write(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
                    f"{user_name} forlod/blev kick’et fra {member.guild.name}, link til {removed['ubiName']} fjernet | Discord ID: {member.id}\n"
                )



async def setup(bot):
    await bot.add_cog(Events(bot))