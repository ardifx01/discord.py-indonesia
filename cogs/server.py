import discord
from discord.ext import commands

class Server(commands.Cog):
    """Kelas untuk mengelola perintah server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="prefix"
    )
    async def prefix(self, ctx: commands.Context, prefix: str):
        """Mengatur prefix untuk server ini."""
        
        if len(prefix) > 3: 
            return await ctx.send("Waduh.. prefix kamu terlalu panjang!")
        
        check = await self.bot.db.fetchrow(
            "SELECT * FROM guildprefix WHERE guild_id = $1", ctx.guild.id
        )
        if check is not None:
            await self.bot.db.execute(
                "UPDATE guildprefix SET prefix = $1 WHERE guild_id = $2", 
                prefix, ctx.guild.id
            )
        else:
            await self.bot.db.execute(
                "INSERT INTO guildprefix VALUES ($1, $2)", 
                ctx.guild.id, prefix
            )
        return await ctx.send(f"Berhasil mengubah prefix menjadi `{prefix}`")

async def setup(bot: commands.Bot):
    await bot.add_cog(Server(bot))