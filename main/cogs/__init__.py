from discord.ext import commands

from .help import Help
from .secret_santa import SecretSanta
from .test import Test


async def cog_setup(bot: commands.Bot, engine):
    await bot.add_cog(Help(bot))
    await bot.add_cog(Test(bot, engine))
    await bot.add_cog(SecretSanta(bot, engine))
