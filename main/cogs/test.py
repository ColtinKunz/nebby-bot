from discord import Member
from discord.ext import commands


class Test(commands.Cog):
    """
    Commands for testing.
    """

    def __init__(self, bot, engine):
        self.engine = engine
        self.bot = bot

    @commands.command()
    async def echo(self, ctx, *args):
        await ctx.send(" ".join(args))

    @commands.command()
    async def test(self, ctx, user: Member = None):
        if not user:
            user = ctx.message.author
        await ctx.send(dict(user.guild_permissions)["administrator"])
