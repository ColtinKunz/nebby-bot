from pathlib import Path

import discord
from yaml import safe_load


def get_config():
    with open(Path("config.yaml")) as config_file:
        return safe_load(config_file)


def get_intents():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    return intents
