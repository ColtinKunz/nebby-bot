import discord
from discord.ext import commands

from utils.components import get_config
from utils.send import send_embed

"""This custom help command is a perfect replacement for the default one on any Discord Bot written in Discord.py!
However, you must put "bot.remove_command('help')" in your bot, and the command must be in a cog for it to work.

Original concept by Jared Newsom (AKA Jared M.F.)
[Deleted] https://gist.github.com/StudioMFTechnologies/ad41bfd32b2379ccffe90b0e34128b8b
Rewritten and optimized by github.com/nonchris
https://gist.github.com/nonchris/1c7060a14a9d94e7929aa2ef14c41bc2

You need to set three variables to make that cog run.
Have a look at line 51 to 57
"""

config = get_config()


class Help(commands.Cog):
    """
    Sends this message!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def help(self, ctx, *input):
        """Shows all sections of that bot"""

        # !SET THOSE VARIABLES TO MAKE THE COG FUNCTIONAL!
        prefix = config["command_prefix"]
        version = config["version"]
        owner = config["owner"]
        bot_name = config["bot_name"]

        # checks if cog parameter was given
        # if not: sending all sections and commands not associated with a cog
        if not input:
            # checks if owner is on this server - used to 'tag' owner
            try:
                owner = ctx.guild.get_member(owner).mention
            except AttributeError:
                owner = owner

            # starting to build embed
            emb = discord.Embed(
                title="Commands and sections",
                color=discord.Color.blue(),
                description=f"Use `{prefix}help <section>` to gain more "
                "information about that section!",
            )

            # iterating trough cogs, gathering descriptions
            cogs_desc = ""
            for cog in self.bot.cogs:
                cogs_desc += f"`{cog}` {self.bot.cogs[cog].__doc__}\n"

            # adding 'list' of cogs to embed
            emb.add_field(name="Sections", value=cogs_desc, inline=False)

            commands_desc = ""
            for command in self.bot.walk_commands():
                # listing command if cog name is None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f"{command.name} - {command.help}\n"

            # adding those commands to embed
            if commands_desc:
                emb.add_field(
                    name="Not belonging to a section",
                    value=commands_desc,
                    inline=False,
                )

            # setting information about author
            emb.add_field(
                name="About",
                value=f"{bot_name} is developed by {owner}.",
            )
            emb.set_footer(text=f"Version {version}")

        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:
            # iterating trough cogs
            for cog in self.bot.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower():

                    # making title - getting description from doc-string below
                    # class
                    emb = discord.Embed(
                        title=f"{cog} - Commands",
                        description=self.bot.cogs[cog].__doc__,
                        color=discord.Color.green(),
                    )

                    # getting commands from cog
                    for command in self.bot.get_cog(cog).get_commands():
                        # if cog is not hidden
                        if not command.hidden:
                            emb.add_field(
                                name=f"`{prefix}{command.name}`",
                                value=command.help,
                                inline=False,
                            )
                    # found cog - breaking loop
                    break
            else:
                emb = discord.Embed(
                    title="What's that?!",
                    description=f"`{input[0]}` unknown.",
                    color=discord.Color.orange(),
                )

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            emb = discord.Embed(
                title="That's too much.",
                description="Please request only one section at once.",
                color=discord.Color.orange(),
            )

        else:
            emb = discord.Embed(
                title="Huh?",
                description=f"Please message {owner} if you got here.",
                color=discord.Color.red(),
            )

        # sending reply embed using our own function defined above
        await send_embed(ctx, emb)
