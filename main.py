import asyncio
import os
import discord
import dotenv
import logging
from logging import DEBUG, Logger

dotenv.load_dotenv()

from discord.ext import commands
from discord import Intents, AllowedMentions
from pathlib import Path
from aiohttp import ClientSession

from utils import database
from utils.logs import setup_logging
import config

log = logging.getLogger("main")

class MyBot(commands.AutoShardedBot):
    """Kelas bot utama yang memperluas AutoShardedBot dari discord.py."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            command_prefix=self.get_prefix,
            intents=Intents.all(),
            owner_id=config.owners_id[0],
            allowed_mentions=AllowedMentions(
                replied_user=False,
                everyone=False,
                roles=False,
                users=True
            ),
            case_insensitive=True,
            max_messages=1500,
        )
        self.db = None
        self.session = None

    async def get_prefix(self, message):
        """Mengembalikan prefix bot."""

        default = config.prefix
        if not message.guild:
            return commands.when_mentioned_or(*default)(self, message)

        guild_prefix = await self.db.fetchval(
            "SELECT prefix FROM guildprefix WHERE guild_id = $1", message.guild.id
        )
        if guild_prefix:
            prefix = guild_prefix
            return commands.when_mentioned_or(*prefix)(self, message)
        else:
            return commands.when_mentioned_or(*default)(self, message)

    async def load_cogs(self):
        """Memuat semua cog dari direktori cogs."""

        cog_files = Path("cogs").glob("*.py")
        
        for file in cog_files:
            if file.name.startswith("_"):
                continue
            
            extension_name = f"cogs.{file.stem}"
            try:
                await self.load_extension(extension_name)
                log.info(f"Loaded extension {extension_name}")
            except Exception as e:
                log.error(f"Failed to load extension {extension_name}: {e}")

    async def setup_hook(self):
        """Memanggil sebelum bot terhubung ke Discord."""

        await self.load_extension("jishaku")
        await self.load_cogs()

        self.db = await database.connect(
            host=os.getenv("DATABASE_HOST"),
            port=os.getenv("DATABASE_PORT"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            database=os.getenv("DATABASE_NAME"),
        )
        self.session = ClientSession()
        log.info("Connected to the database and initialized HTTP session.")
    
    async def on_ready(self):
        """Memanggil kapan bot telah siap."""

        log.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message) -> None:
        """
        Memproses pesan yang diterima.
        """

        if message.author == self.user or message.author.bot:
            return
        
        await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Menangani kesalahan yang terjadi saat menjalankan perintah."""

        if isinstance(error, commands.CheckFailure):
            return await ctx.reply(error)
        if isinstance(error, commands.CommandNotFound):
            return await ctx.send(error)
        if isinstance(error, commands.MissingPermissions):
            return await ctx.reply(
                embed=discord.Embed(
                    description="Kamu kehilangan akses: " + 
                    ", ".join(error.missing_permissions)
                )
            )
        if isinstance(error, commands.BotMissingPermissions):
            return await ctx.reply(
                embed=discord.Embed(
                    description="Saya kehilangan akses: " + ", ".join(error.missing_perms)
                )
            )
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                description=f"Argumen yang diperlukan `<{error.param.name}>`")
            if ctx.command.usage:
                embed.add_field(name="Usage", value=f"```bf\n{ctx.command.usage}```")
            return await ctx.reply(embed=embed)


async def main():
    """Utama Fungsi utama untuk menjalankan bot."""

    setup_logging(DEBUG)
    
    bot = MyBot()
    await bot.start(token=os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Kamu sudah menghentikan bot.")