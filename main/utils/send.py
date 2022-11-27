from discord.errors import Forbidden


async def send_embed(ctx, embed):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send(
                "Hey, seems like I can't send embeds. "
                "Please check my permissions :)"
            )
        except Forbidden:
            await ctx.author.send(
                "Hey, seems like I can't send any message in "
                f"{ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue?",
                embed=embed,
            )
