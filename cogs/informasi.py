import discord
from discord.ext import commands

class Informasi(commands.Cog):
    """Kelas untuk mengelola perintah informasi."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="botinfo"
    )
    async def botinfo(self, ctx: commands.Context):
        """Menampilkan informasi tentang bot."""
        embed = discord.Embed(
            title="Informasi Bot",
            description="Ini adalah bot contoh yang dibuat dengan discord.py",
            color=discord.Color.blue()
        )
        embed.add_field(name="Nama Bot", value=self.bot.user.name, inline=True)
        embed.add_field(name="ID Bot", value=self.bot.user.id, inline=True)
        embed.add_field(name="Pengembang", value="zakilla", inline=True)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Informasi(bot))