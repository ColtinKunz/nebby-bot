from random import choice

from discord import Embed, Forbidden
from discord.ext import commands
from sqlalchemy.orm import Session

from models import (
    User,
    SecretSantaEvent,
    UserSecretSantaEvent,
    SecretSantaAssignment,
)
from utils.model import get, get_or_create, create
from utils.send import send_embed


class SecretSanta(commands.Cog):
    """
    Commands for testing.
    """

    def __init__(self, bot, engine):
        self.engine = engine
        self.bot = bot

    @commands.command()
    async def my_events(self, ctx):
        with Session(self.engine) as session:
            user = get(
                session,
                User,
                discord_user_id=str(ctx.author.id),
                discord_server_id=str(ctx.guild.id),
            )
            embed = Embed(
                title=f"`{ctx.author.display_name}`'s Secret Santa Events",
            )
            embed.set_thumbnail(url=ctx.author.display_avatar)
            if user.secret_santa_events:
                current_events = [
                    ss_event
                    for ss_event in user.secret_santa_events
                    if ss_event.ongoing
                ]
                for ss_event in current_events:
                    embed.add_field(
                        name=ss_event.name,
                        value=f"{ss_event!r}",
                    )
            else:
                current_events = []
                embed.description = "No current events."
            await send_embed(ctx, embed)
            return current_events

    @commands.command()
    async def my_previous_events(self, ctx):
        with Session(self.engine) as session:
            user = get(
                session,
                User,
                discord_user_id=str(ctx.author.id),
                discord_server_id=str(ctx.guild.id),
            )
            embed = Embed(
                title=f"`{ctx.author.display_name}`'s Previous Secret Santa "
                "Events",
            )
            embed.set_thumbnail(url=ctx.author.display_avatar)
            if user.secret_santa_events:
                previous_events = [
                    ss_event
                    for ss_event in user.secret_santa_events
                    if not ss_event.ongoing
                ]
                for ss_event in previous_events:
                    embed.add_field(
                        name=ss_event.name,
                        value=f"{ss_event!r}",
                    )
            else:
                previous_events = []
                embed.description = "No finished events."
            await send_embed(ctx, embed)
            return previous_events

    @commands.command()
    async def create_event(self, ctx, *name):
        name = " ".join(name)
        with Session(self.engine) as session:
            user = get(
                session,
                User,
                discord_user_id=str(ctx.author.id),
                discord_server_id=str(ctx.guild.id),
            )
            if not user:
                await ctx.send(
                    f"No user found with ID `{user.discord_user_id}`."
                )
                return
            event, created = get_or_create(
                session, SecretSantaEvent, name=name, owner=user, ongoing=True
            )
            if not created:
                await ctx.send("Event with this name already exists.")
                return
            event.user_associations.append(UserSecretSantaEvent(user=user))
            await ctx.send(
                f"Created new Secret Santa Event with the name `{name}`."
            )
            return event.id

    @commands.command()
    async def set_previous_event(
        self, ctx, this_event_id: int, other_event_id: int
    ):
        with Session(self.engine) as session:
            this_event = get(
                session,
                SecretSantaEvent,
                id=str(this_event_id),
                ongoing=True,
            )
            if not this_event:
                await ctx.send(f"No event found with ID `{this_event_id}`.")
                return
            other_event = get(
                session,
                SecretSantaEvent,
                id=str(other_event_id),
            )
            if not other_event:
                await ctx.send(f"No event found with ID `{other_event_id}`.")
                return
            if other_event.ongoing:
                await ctx.send(f"`{other_event.name}` is still ongoing.")
                return
            this_event.previous_event = other_event
            session.add(this_event)
            session.commit()
            await ctx.send(
                f"Set `{other_event.name}` as previous event "
                f"`{this_event.name}`."
            )

    @commands.command()
    async def add_user_to_event(self, ctx, event_id, user_id):
        with Session(self.engine) as session:
            event = get(session, SecretSantaEvent, id=event_id, ongoing=True)
            if not event:
                await ctx.send(f"No event found with ID `{event_id}`.")
                return
            user = get(
                session,
                User,
                discord_user_id=user_id,
                discord_server_id=str(ctx.guild.id),
            )
            if not user:
                await ctx.send(f"No user found with ID `{user_id}`.")
                return
            if user in event.users:
                await ctx.send(f"User already part of event `{event_id}`.")
                return
            event.user_associations.append(UserSecretSantaEvent(user=user))
            session.add(event)
            session.commit()
            await ctx.send(f"Added `{user.name}` to `{event.name}`.")

    @commands.command()
    async def remove_user_from_event(self, ctx, event_id, user_id):
        with Session(self.engine) as session:
            event = get(session, SecretSantaEvent, id=event_id, ongoing=True)
            if not event:
                await ctx.send(f"No event found with ID `{event_id}`.")
                return
            user = get(
                session,
                User,
                discord_user_id=user_id,
                discord_server_id=str(ctx.guild.id),
            )
            if not user:
                await ctx.send(f"No user found with ID `{user_id}`.")
                return
            user_association = get(
                session,
                UserSecretSantaEvent,
                secret_santa_event=event,
                user=user,
            )
            if not user_association:
                await ctx.send(
                    f"No association found between user with ID `{user_id}` "
                    f"and event with ID `{event_id}`."
                )
                return
            session.delete(user_association)
            session.commit()
            await ctx.send(f"Removed `{user.name}` from `{event.name}`.")

    @commands.command()
    async def start_event(self, ctx, event_id):
        with Session(self.engine) as session:
            event = get(
                session,
                SecretSantaEvent,
                id=event_id,
            )
            if not event:
                await ctx.send(f"No event found with ID `{event_id}`.")
                return
            santa_assigns = []
            for user in event.users:
                user_pool = [
                    potential_user_assignment
                    for potential_user_assignment in event.users
                    if user != potential_user_assignment
                    and (
                        (
                            event.previous_event
                            and len(
                                [
                                    assign
                                    for assign in event.previous_event.secret_santa_assignments
                                    if assign.from_user == user
                                    and assign.to_user
                                    == potential_user_assignment
                                ]
                            )
                            == 0
                        )
                        or not event.previous_event
                    )
                    and potential_user_assignment
                    not in [assign.to_user for assign in santa_assigns]
                ]
                user_assignment = choice(user_pool)
                santa_assigns.append(
                    create(
                        session,
                        SecretSantaAssignment,
                        from_user=user,
                        to_user=user_assignment,
                        secret_santa_event=event,
                    )
                )
            session.add_all(santa_assigns)
            session.commit()
            for assign in santa_assigns:
                discord_user = await self.bot.fetch_user(
                    assign.from_user.discord_user_id
                )
                try:
                    await discord_user.send(
                        f"You got `{assign.to_user.name}` for "
                        f"`{event.name}` on `{ctx.guild.name}`"
                    )
                except Forbidden:
                    with open(f"{assign.from_user.name}.txt", "w") as file:
                        file.write(
                            f"You got `{assign.to_user.name}` for "
                            f"`{event.name}` on `{ctx.guild.name}`"
                        )
            await ctx.send(
                f"Sent all secret santa notifications for `{event.name}`."
            )

    @commands.command()
    async def finish_event(self, ctx, event_id):
        with Session(self.engine) as session:
            event = get(
                session,
                SecretSantaEvent,
                id=event_id,
            )
            if not event:
                await ctx.send(f"No event found with ID `{event_id}`.")
                return
            if str(event.owner.discord_user_id) != str(ctx.author.id):
                await ctx.send("You cannot finish an event you do not own.")
                return
            event.ongoing = False
            session.add(event)
            session.commit()
            await ctx.send(f"Finished `{event.name}`.")

    @commands.command()
    async def iterate_event(self, ctx, event_id, *next_event_name):
        await ctx.invoke(
            self.bot.get_command("finish_event"),
            event_id=event_id,
        )
        new_event_id = await ctx.invoke(
            self.bot.get_command("create_event"),
            *next_event_name,
        )
        await ctx.invoke(
            self.bot.get_command("set_previous_event"),
            this_event_id=new_event_id,
            other_event_id=event_id,
        )
        with Session(self.engine) as session:
            previous_event = get(session, SecretSantaEvent, id=event_id)
            for user in previous_event.users:
                await ctx.invoke(
                    self.bot.get_command("add_user_to_event"),
                    event_id=new_event_id,
                    user_id=str(user.discord_user_id),
                )
