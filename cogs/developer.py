import discord
from discord.ext import commands

class Developer(commands.Cog):
    """Kelas untuk perintah-perintah yang berkaitan dengan pengembangan"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.command(
        name="reload"
    )
    async def reload(self, ctx, extension: str):
        """Memuat ulang ekstensi."""
        try:
            self.bot.reload_extension(extension)
            await ctx.send(f"Ekstensi `{extension}` berhasil dimuat ulang.")
        except Exception as e:
            await ctx.send(f"Terjadi kesalahan saat memuat ulang ekstensi `{extension}`: {e}")

async def setup(bot):
    await bot.add_cog(Developer(bot))