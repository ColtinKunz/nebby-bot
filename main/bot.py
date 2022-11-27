import logging
import os
import sys
from asyncio import run as async_run
from pathlib import Path


from dotenv import load_dotenv
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from cogs import cog_setup
from models import Base, User
from utils.components import get_config, get_intents
from utils.logs import get_date_file_name
from utils.model import get_or_create, get

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

config = get_config()
command_prefix = config["command_prefix"]
bot = commands.Bot(command_prefix=command_prefix, intents=get_intents())
engine = create_engine("sqlite:///database.db")
Base.metadata.create_all(engine)

###########################################################################
# Referenced from https://stackoverflow.com/a/16993115
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
    )


sys.excepthook = handle_exception
###########################################################################
logs_dir = Path(config["logs_dir"])
if not logs_dir.exists():
    logs_dir.mkdir()
logging.basicConfig(
    filename=logs_dir / f"{get_date_file_name()}.log",
    level=logging.getLevelName("INFO"),
    format="%(asctime)s :: %(levelname)-8s \n\t%(message)s",
)


handler = logging.FileHandler(
    filename=logs_dir / f"{get_date_file_name()}.log",
    encoding="utf-8",
    mode="w",
)

bot.remove_command("help")


@bot.event
async def on_ready():
    member = await bot.fetch_user(config["owner_id"])
    await member.send("I am awake.")

    with Session(engine) as session:
        for guild in bot.guilds:
            guild_members = [
                member for member in guild.members if not member.bot
            ]
            for member in guild_members:
                user, _ = get_or_create(
                    session,
                    User,
                    discord_user_id=member.id,
                    discord_server_id=guild.id,
                    name=member.display_name,
                )


@bot.event
async def on_member_update(before, after):
    with Session(engine) as session:
        user = get(session, User, discord_user_id=before.id)
        user.name = after.display_name
        session.add(user)
        session.commit()
        logging.info(f"{after.id} updated display name to {user.name}.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("That command wasn't found.")
    elif isinstance(error, commands.errors.CommandError):
        await ctx.send(
            "Unhandled command error. Please report this to an admin!"
        )
        logging.error(error)
    else:
        await ctx.send(
            "Something weird happened. Please report this to an admin!"
        )
        logging.error(error)


async def main():
    async with bot:
        await cog_setup(bot, engine)
        await bot.start(BOT_TOKEN)


async_run(main())
