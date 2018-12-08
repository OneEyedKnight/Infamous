import discord
import asyncio
import random
from discord.ext import commands
from .utils import rpg_tools as rpg
from .utils import checks
from .utils.paginator import SimplePaginator

monologue = """
The year is 2033; technology has become advanced, what was once science fiction
has become a reality. Years of research and experimentation have created superhumans.

In 2029 a rogue scientist by name of Angus Kleric had developed a software that created 
pills to genetically enhance a human; many people have taken the pills and gave themselves 
superpowers, however it caused them to become insane and use their abilities for
committing crime. 

The drug had been discontinued, but new illegal versions of it were made. 
This opted the U.S Government to make their own superhumans; superheroes to combat evil supervillians; 
the term used for the ones who took the Kleric drug.

You can be a superhero or supervillian and interact in the city of Sterben 
where you can take on other superheroes or supervillians.
            """
shop_items = {"Super Strength": [12000, 'https://imgur.com/vbtnxdi.png',
                                 "Allows you to lift 10x your weight.", 250, 300],

              "Flight": [15000, 'https://imgur.com/jr8CyIk.png',
                         "Allows you to fly without an aircraft.", 200, 250],

              "Telekinesis": [18000, 'https://imgur.com/2UWGYBq.png',
                              "Control objects with your mind.", 300, 350],

              "Super Speed": [21000, 'https://imgur.com/bBJujmH.png',
                              "Run faster than a speeding bullet.", 280, 330],

              "Super Intelligence": [24000, 'https://imgur.com/k9V9ywi.png',
                                     "Outsmart your opponents.", 180, 230],

              "Fast Regeneration": [27000, 'https://imgur.com/97ZtaFe.gif',
                                    "Wounds won't stop you.", 220, 270],

              "Heat Vision": [30000, 'https://imgur.com/fV8pIJo.png',
                              "Destroy things with your vision.", 320, 370],

              "Telepathy": [33000, 'https://imgur.com/0gbfMDG.png',
                            "Control other people's minds.", 100, 150],

              "Invisibility": [36000, 'https://imgur.com/v6MbTV5.gif',
                               "Become the ultimate spy.", 120, 170],

              "Freeze Breath": [39000, 'https://imgur.com/ot2zakO.gif',
                                "Freeze things with your breath.", 350, 400],

              "Sonic Scream": [41000, 'https://imgur.com/El8Xh9Y.gif',
                               "Break glass with just your voice.", 400, 450],

              "Electrokinesis": [44000, 'https://imgur.com/Y8eBb18.png',
                                 "Harness the power of electricity.", 420, 470]}


class Rpg2:
    """2nd version of Infamous RPG"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.unregistered2()
    async def register(self, ctx):
        """Become apart of a world filled with superhumans"""

        await ctx.send(monologue)

        abilities = ["Super Strength", "Flight", "Telekinesis",
                     "Super Speed", "Super Intelligence", "Fast Regeneration",
                     "Heat Vision", "Telepathy", "Invisibility",
                     "Freeze Breath", "Sonic Scream", "Electrokinesis"]

        await ctx.send(f"Choose an ability (You will be able to gain more abilities as you acquire more money). \n"
                       f"```prolog\n{', '.join(abilities)}.```")

        async def check(m):
            return m.author == ctx.author and m.content.title() in abilities

        active = True
        while active:
            try:
                msg = (await self.bot.wait_for('message', check=check, timeout=60)).content.title()
            except asyncio.TimeoutError:
                return await ctx.send("Registration cancelled.")

            if msg not in abilities:
                await ctx.send(f"{ctx.author.mention} Pick a ability from the list!")
            else:
                await ctx.send(f"Your main ability is: **{msg}** \n"
                               f"You can acquire more abilities in the shop and you can master your abilities")

                async with self.bot.db.acquire() as db:
                    await db.execute("INSERT INTO profiles VALUES($1, $2, $3, $4, $5)",
                                     ctx.author.id, 1, 0, 0, msg)
                    await db.execute("INSERT INTO abilities VALUES($1, $2, $3, $4, $5, $6)",
                                     ctx.author.id, msg, 1, 0, shop_items[msg][3], shop_items[msg][4])

                await ctx.send("You have successfully been registered.")
                active = False

    @commands.command(aliases=['quest', 'adv'])
    @commands.cooldown(1, 600, commands.BucketType.user)
    @checks.registered2()
    async def adventure(self, ctx):
        """Patrol the streets to get rewards."""

        mission_ = ['mission']
        for i in mission_:
            cmd = self.bot.get_command(i)
            if cmd.is_on_cooldown(ctx):
                await ctx.send(f"You can't use `{ctx.prefix}mission` and `{ctx.prefix}adventure` at the same time.")
                ctx.command.reset_cooldown(ctx)
                return

        await ctx.send("You went on a adventure; you will return in 10 minutes.")
        await asyncio.sleep(600)
        money = random.randint(20, 100)
        xp = random.randint(20, 100)
        await ctx.send(random.choice([
            f'You stopped a robbery and apprehended a supervillian; you were rewarded with ${money} and {xp}xp.',
            f'You defeated a supervillian and stole their ${money} and {xp}xp.',
            f'You defeated a superhero and stole their ${money} and {xp}xp.',
            f'You saved many civilians from an attack from a supervillian; you earned ${money} and {xp}xp.',
            f'You lured a superhero to your trap and killed them; you earned ${money} and {xp}xp.',
            f'You foiled a supervillian\'s plan to destroy the world; you earned ${money} and {xp}xp.']))

        await rpg.level2(ctx, money, xp)
        await rpg.guild_level(ctx, xp)

    @commands.command(aliases=['p'])
    async def profile(self, ctx, user: discord.Member = None):
        """View the stats of fellow superhumans."""
        if not user:
            user = ctx.author
        stats = (await rpg.fetch_user2(ctx, user))
        async with ctx.bot.db.acquire() as db:
            abilities_ = await db.fetch("SELECT * FROM abilities WHERE id=$1", user.id)

        ability = []
        for i in abilities_:
            if i[1] == stats[4]:
                main = f"{i[1]} - Level {i[2]}"
            else:
                ability.append(f"**{i[1]}** - Level {i[2]}")

        if ability:
            ability = '\n'.join(ability)
        else:
            ability = 'None'
        await ctx.send(embed=discord.Embed(color=self.bot.embed_color, description=f"Accumulated XP: {stats[2]}")
                       .set_author(name=f"{user.display_name} | Level {stats[1]}", icon_url=user.avatar_url)
                       .add_field(name="Info", value=f"**Main Ability:** {main} \n"
                                                     f"**Balance:** {stats[3]}")
                       .add_field(name="Other Abilities", value=ability, inline=False)
                       )

    @commands.command()
    @checks.registered2()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def mission(self, ctx):
        """Participate in an assigned mission."""

        adventure_ = ['adventure']
        for i in adventure_:
            cmd = self.bot.get_command(i)
            if cmd.is_on_cooldown(ctx):
                await ctx.send(f"You can't use `{ctx.prefix}{ctx.command}` and `{ctx.prefix}{i}` at the same time.")
                ctx.command.reset_cooldown(ctx)
                return

        mission = random.choice([
            "Gather intel about a infamous supervillian gang.",
            "Attack the Scientific and Technological Advanced Research Laboratory.",
            "Defeat the infamous level 70 supervillian Solaris.",
            "Defeat the famous level 75 superhero Chronos.",
            "Save the life of Chronos; who was badly injured in a fight with Solaris.",
            "Save the life of Solaris; who was badly injured in a fight with Chronos.",
            "Stop a Kleric drug deal from happening."
        ])
        await ctx.send(f"**You've been sent to:** {mission} \nYou will return in 15 minutes.")
        await asyncio.sleep(900)
        money = random.randint(100, 250)
        xp = random.randint(100, 250)
        await ctx.send(f"You have been awarded ${money} and {xp}xp for completing the mission.")
        await rpg.level2(ctx, money, xp)
        await rpg.guild_level(ctx, xp)

    @commands.command()
    @checks.registered2()
    async def shop(self, ctx):
        """Acquire new abilities"""

        p = []
        number = 0
        abilities = await rpg.fetch_abilities(ctx)
        shop = [x for x in shop_items if x not in abilities]
        if shop:
            for i in shop:
                number += 1
                p.append(rpg.ability_embed(ctx, shop_items, i, number, len(shop)))

            await SimplePaginator(extras=p).paginate(ctx)
        else:
            await ctx.send("You have acquired every ability in the shop!")

    @commands.command()
    @checks.registered2()
    async def acquire(self, ctx, *, ability):
        """Buy new abilities from the shop."""

        user = (await rpg.fetch_user2(ctx))
        abilities = await rpg.fetch_abilities(ctx)
        if ability.title() in abilities:
            return await ctx.send(f"You already have this ability, use `{ctx.prefix}master <ability>`")

        if user[3] >= shop_items[ability.title()][0]:
            async with ctx.bot.db.acquire() as db:
                await db.execute("INSERT INTO abilities VALUES($1, $2, $3, $4, $5, $6)",
                                 ctx.author.id, ability.title(), shop_items[ability.title()][3],
                                 shop_items[ability.title()][4])

                await db.execute("UPDATE profiles SET bal = bal - $1 WHERE id=$2",
                                 shop_items[ability.title()][0], ctx.author.id)

            await ctx.send(f"**You have acquired:** {ability.title()}",
                           embed=discord.Embed(color=self.bot.embed_color, description=shop_items[ability.title()][2])
                           .set_author(name=f"You have acquired: {ability.title()}")
                           .set_image(url=shop_items[ability.title()][1])
                           )
        else:
            await ctx.send(f"{ctx.author.mention} you need ${shop_items[ability.title()][0] - user[3]} more to acquire"
                           f" **{ability.title()}**.")

    @commands.command()
    @checks.registered2()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def loot(self, ctx):
        """Get hourly loot."""

        loot_ = ['adventure', 'mission']
        for i in loot_:
            cmd = self.bot.get_command(i)
            if cmd.is_on_cooldown(ctx):
                await ctx.send(f"You cannot use `{ctx.prefix}{ctx.command}` and `{ctx.prefix}{i}`")
                ctx.command.reset_cooldown(ctx)
                return

        await ctx.send("You have been given $250 and 250xp")
        await rpg.level2(ctx, 250, 250)
        await rpg.guild_level(ctx, 250)

    @commands.command()
    @checks.registered2()
    @commands.cooldown(1, 84600, commands.BucketType.user)
    async def daily(self, ctx):
        """Get daily loot."""
        daily_ = ['adventure', 'mission']
        for i in daily_:
            cmd = self.bot.get_command(i)
            if cmd.is_on_cooldown(ctx):
                await ctx.send(f"You can't use `{ctx.prefix}{ctx.command}` and `{ctx.prefix}{i}` at the same time.")
                return

        await ctx.send("You have been given $500 and 500xp")
        await rpg.level2(ctx, 500, 500)
        await rpg.guild_level(ctx, 500)

    @commands.command()
    @checks.registered2()
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def master(self, ctx):
        """Upgrade your abilities."""

        abilities = await rpg.fetch_abilities(ctx)
        user = (await rpg.fetch_user2(ctx))
        await ctx.send(f"Choose an ability to master: {','.join(abilities)}")

        def check(m):
            return m.author == ctx.author and m.content.title() in abilities

        try:
            msg = (await ctx.bot.wait_for('message', check=check, timeout=15)).content.title()
        except asyncio.TimeoutError:
            return await ctx.send("I guess you don't want to pick an ability.")

        if user[3] >= shop_items[msg][0] / 4:
            async with ctx.bot.db.acquire() as db:
                await db.execute("UPDATE profiles SET bal = bal - $1 WHERE id = $2",
                                 shop_items[msg][0] / 4, ctx.author.id)

            choice = random.choice(["Low", "Middle", "Greater"])
            if choice == "Low":
                xp = random.randint(20, 100)
                await ctx.send(f"You earned {xp}xp and added 50 points to your {msg} stats.")
                await rpg.ability_level(ctx, xp, 50, 50, msg)
            elif choice == "Middle":
                xp = random.randint(100, 250)
                await ctx.send(f"You earned {xp}xp and added 100 points to your {msg} stats.")
                await rpg.ability_level(ctx, xp, 100, 100, msg)
            else:
                xp = random.randint(150, 300)
                await ctx.send(f"You earned {xp}xp and added 150 points to your {msg} stats")
                await rpg.ability_level(ctx, xp, 150, 150, msg)
        else:
            return await ctx.send(f"{ctx.author.mention} you need ${shop_items[msg][0] / 4 - user[3]} more to master.")

    @commands.command()
    @checks.registered2()
    async def active(self, ctx):
        """Shows all the active cooldowns."""

        p = []
        for command in self.bot.get_cog_commands("Infamous RPG v2"):
            if command.is_on_cooldown(ctx):
                p.append(command.name)

        await ctx.send(f"**Commands currently on cooldown for {ctx.author.mention}:** {', '.join(p)}")

    @commands.command()
    @checks.registered2()
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def gamble(self, ctx):
        """Risk winning it all or losing it all."""

        await ctx.send("How much are you willing to gamble?")

        user = (await rpg.fetch_user2(ctx))

        def check(m):
            return m.author == ctx.author and m.content.isdigit()

        active = True
        while active:
            try:
                msg = (await ctx.bot.wait_for('message', check=check, timeout=15)).content
            except asyncio.TimeoutError:
                return await ctx.send("I guess you don't want to risk it.")

            if int(msg) >= user[3]:
                await ctx.send(f"{ctx.author.mention} you can't gamble what you don't have.")
            else:
                choice = random.choice(["Win", "Lose"])
                async with ctx.bot.db.acquire() as db:
                    if choice == "Win":
                        await ctx.send(f"{ctx.author.mention} got ${msg} richer!")
                        await db.execute("UPDATE profiles SET bal = bal + $1 WHERE id=$2", int(msg), ctx.author.id)
                    else:
                        await ctx.send(f"{ctx.author.mention} got ${msg} poorer")
                        await db.execute("UPDATE profiles SET bal = bal - $1 WHERE id=$2", int(msg), ctx.author.id)
                active = False

    @commands.command()
    @checks.registered2()
    @commands.cooldown(1, 600, commands.BucketType.channel)
    async def duel(self, ctx, user: checks.SuperhumanFinder=None):
        """Battle other players."""

        if not user:
            await ctx.send(f"You need to pick someone.")
            ctx.command.reset_cooldown(ctx)
            return

        user = ctx.guild.get_member_named(user)
        abilities1 = await rpg.fetch_abilities(ctx)
        abilities2 = await rpg.fetch_abilities(ctx, user)

        if len(abilities1 or abilities2) <= 2:
            await ctx.send("One of you don't have two or more abilities")
            ctx.command.reset_cooldown(ctx)
            return

        await ctx.send("Do you accept this challenge? `Yes` or `No`")
        yon = await rpg.yon(ctx, user=user)
        if yon == "Yes":
            await ctx.send(f"{ctx.author.mention} Which two abilities do you choose to fight with? \n"
                           f"{', '.join(abilities1)}. (Type your choice like this: Super Speed, Telekinesis)")

            def check(m):
                return m.author == ctx.author and m.content in abilities1

            def check2(m):
                return m.author == user and m.content in abilities2

            try:
                msg = (await ctx.bot.wait_for('message', check=check, timeout=15)).content.title()
            except asyncio.TimeoutError:
                return await ctx.send(f"{ctx.author.mention}, you ran out of time.")

            await ctx.send(f"{user.mention} Which two abilities do you choose to fight with? \n"
                           f"{', '.join(abilities1)}. (Type your choice like this: Super Speed, Telekinesis)")

            try:
                msg2 = (await ctx.bot.wait_for('message', check=check2, timeout=15)).content.title()
            except asyncio.TimeoutError:
                return await ctx.send(f"{ctx.author.mention}, you ran out of time.")

            async with ctx.bot.db.acquire() as db:
                skill1_ = await db.fetchrow("SELECT * FROM abilities WHERE id=$1 AND ability=$2", ctx.author.id,
                                            (msg.split(', '))[0])
                skill2_ = await db.fetchrow("SELECT * FROM abilities WHERE id=$1 AND ability=$2", ctx.author.id,
                                            (msg.split(', '))[1])
                skill1 = await db.fetchrow("SELECT * FROM abilities WHERE id=$1 AND ability=$2", user.id,
                                           (msg2.split(', '))[0])
                skill2 = await db.fetchrow("SELECT * FROM abilities WHERE id=$1 AND ability=$2", user.id,
                                           (msg2.split(', '))[1])

            hp = skill1_[5] + skill2_[5]
            hp2 = skill1[5] + skill2[5]
            active = True
            await ctx.send(f"{ctx.author.mention} pick an ability: {msg}")
            while active:
                def player1(m):
                    return m.author == ctx.author and m.content in [skill1_[0], skill2_[0]]

                def player2(m):
                    return m.author == user and m.content in [skill1[0], skill2[0]]

                try:
                    msg_ = (await ctx.bot.wait_for('message', check=player1, timeout=30)).content
                except asyncio.TimeoutError:
                    return await ctx.send(f"{ctx.author.mention} has been disqualified. Duel is over!")
                else:
                    if msg_ == skill1_[0]:
                        dmg = random.randint(10, skill1_[4] / 2)
                        if dmg > hp2 / 2:
                            chance = random.choice(["Hit", "Miss"])
                            hp2 = hp2 - dmg
                            if chance == "Hit":
                                await ctx.send(
                                    f"{ctx.author.mention} Your attack using your {skill1_[0]} has dealt {dmg}dmg \n"
                                    f"{user.mention} has {hp2}hp.")
                            else:
                                hp = hp - dmg
                                await ctx.send(
                                    f"{ctx.author.mention} missed! Causing {user.mention} to deal {dmg}dmg \n"
                                    f"They now have {hp}hp.")
                        else:
                            chance = random.choice(["Hit", "Miss"])
                            hp2 = hp2 - dmg
                            if chance == "Hit":
                                await ctx.send(
                                    f"{ctx.author.mention} Your attack using your {skill1_[0]} has dealt {dmg}dmg \n"
                                    f"{user.mention} has {hp2}hp.")
                            else:
                                hp = hp - dmg
                                await ctx.send(
                                    f"{ctx.author.mention} missed! Causing {user.mention} to deal {dmg}dmg \n"
                                    f"They now have {hp}hp.")
                        if hp2 <= 0:
                            xp = random.randint(250, 500)
                            mon = random.randint(250, 500)
                            await ctx.send(f"{ctx.author.mention} wins! They earn {xp}xp and ${mon}")
                            await rpg.level2(ctx, mon, xp)
                            await rpg.guild_level(ctx, xp)
                            active = False
                    else:
                        dmg = random.randint(10, skill2_[4] / 2)
                        if dmg > hp2 / 2:
                            chance = random.choice(["Hit", "Miss"])
                            hp2 = hp2 - dmg
                            if chance == "Hit":
                                await ctx.send(
                                    f"{ctx.author.mention} Your attack using your {skill2_[0]} has dealt {dmg}dmg \n"
                                    f"{user.mention} has {hp2}hp.")
                            else:
                                hp = hp - dmg
                                await ctx.send(
                                    f"{ctx.author.mention} missed! Causing {user.mention} to deal {dmg}dmg \n"
                                    f"They now have {hp}hp.")
                        else:
                            chance = random.choice(["Hit", "Miss"])
                            hp2 = hp2 - dmg
                            if chance == "Hit":
                                await ctx.send(
                                    f"{ctx.author.mention} Your attack using your {skill2_[0]} has dealt {dmg}dmg \n"
                                    f"{user.mention} has {hp2}hp.")
                            else:
                                hp = hp - dmg
                                await ctx.send(
                                    f"{ctx.author.mention} missed! Causing {user.mention} to deal {dmg}dmg \n"
                                    f"They now have {hp}hp.")
                        if hp2 <= 0:
                            xp = random.randint(250, 500)
                            mon = random.randint(250, 500)
                            await ctx.send(f"{ctx.author.mention} wins! They earn {xp}xp and ${mon}")
                            await rpg.level2(ctx, mon, xp)
                            await rpg.guild_level(ctx, xp)
                            active = False

                try:
                    msg_ = (await ctx.bot.wait_for('message', check=player2, timeout=30)).content
                except asyncio.TimeoutError:
                    return await ctx.send(f"{user.mention} has been disqualified. Duel is over!")
                else:
                    if msg_ == skill1[0]:
                        dmg = random.randint(10, skill1[4] / 2)
                        if dmg > hp2 / 2:
                            chance = random.choice(["Hit", "Miss"])
                            hp2 = hp2 - dmg
                            if chance == "Hit":
                                await ctx.send(
                                    f"{ctx.author.mention} Your attack using your {skill1[0]} has dealt {dmg}dmg \n"
                                    f"{user.mention} has {hp2}hp.")
                            else:
                                hp = hp - dmg
                                await ctx.send(
                                    f"{ctx.author.mention} missed! Causing {user.mention} to deal {dmg}dmg \n"
                                    f"They now have {hp}hp.")
                        else:
                            chance = random.choice(["Hit", "Miss"])
                            hp2 = hp2 - dmg
                            if chance == "Hit":
                                await ctx.send(
                                    f"{ctx.author.mention} Your attack using your {skill1[0]} has dealt {dmg}dmg \n"
                                    f"{user.mention} has {hp2}hp.")
                            else:
                                hp = hp - dmg
                                await ctx.send(
                                    f"{user.mention} missed! Causing {ctx.author.mention} to deal {dmg}dmg \n"
                                    f"They now have {hp}hp.")
                        if hp <= 0:
                            xp = random.randint(250, 500)
                            mon = random.randint(250, 500)
                            await ctx.send(f"{user.mention} wins! They earn {xp}xp and ${mon}")
                            await rpg.level2(ctx, mon, xp, user)
                            await rpg.guild_level(ctx, xp, user)
                            active = False
                    else:
                        dmg = random.randint(10, skill2[4] / 2)
                        if dmg > hp2 / 2:
                            chance = random.choice(["Hit", "Miss"])
                            hp2 = hp2 - dmg
                            if chance == "Hit":
                                await ctx.send(
                                    f"{user.mention} Your attack using your {skill2[0]} has dealt {dmg}dmg \n"
                                    f"{ctx.author.mention} has {hp2}hp.")
                            else:
                                hp = hp - dmg
                                await ctx.send(
                                    f"{user.mention} missed! Causing {ctx.author.mention} to deal {dmg}dmg \n"
                                    f"They now have {hp}hp.")
                        else:
                            chance = random.choice(["Hit", "Miss"])
                            hp2 = hp2 - dmg
                            if chance == "Hit":
                                await ctx.send(
                                    f"{user.mention} Your attack using your {skill2[0]} has dealt {dmg}dmg \n"
                                    f"{ctx.author.mention} has {hp2}hp.")
                            else:
                                hp = hp - dmg
                                await ctx.send(
                                    f"{user.mention} missed! Causing {ctx.author.mention} to deal {dmg}dmg \n"
                                    f"They now have {hp}hp.")
                        if hp2 <= 0:
                            xp = random.randint(250, 500)
                            mon = random.randint(250, 500)
                            await ctx.send(f"{user.mention} wins! They earn {xp}xp and ${mon}")
                            await rpg.level2(ctx, mon, xp, user)
                            await rpg.guild_level(ctx, xp, user)
                            active = False
        else:
            return await ctx.send("I guess you don't want to duel.")

    @duel.error
    async def duel_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"{ctx.author.mention} there is currently a active duel in {ctx.channel.mention}")

        elif isinstance(error, commands.BadArgument):
            return await ctx.send(error)

    @commands.command()
    async def top(self, ctx):
        """The Top players."""

        async with ctx.bot.db.acquire() as db:
            lb = await db.fetch("SELECT * FROM profiles ORDER BY xp DESC")

        p = []
        number = 0
        for user in lb:
            try:
                user_ = ctx.guild.get_member(user[0])
            except discord.HTTPException:
                user_ = ctx.bot.get_user(user[0])

            number += 1
            p.append(discord.Embed(color=self.bot.embed_color, description=f"**Total XP:** {user[2]}")
                     .set_author(name=f"#{number} {user_.display_name or user_.name}| Level {user[1]}")
                     .set_image(url=user_.avatar_url_as(static_format="png", size=1024))
                     .set_footer(text=f"Page {number} of {len(lb)}")
                     )

        await SimplePaginator(extras=p).paginate(ctx)

    @commands.command()
    @checks.registered2()
    @commands.cooldown(1, 600, commands.BucketType.channel)
    async def drink(self, ctx, user: checks.SuperhumanFinder):
        if not user:
            return await ctx.send("Find a reasonable drinking partner")

        user = ctx.guild.get_member_named(user)

        yon = await rpg.yon(ctx, user)
        await asyncio.sleep(60)
        if yon == "Yes":
            choice = random.choice([ctx.author, user])
            xp = random.randint(100, 200)
            mon = random.randint(100, 200)
            if choice == ctx.author:
                await ctx.send(f"{ctx.author.mention} wins the drinking contest!")
                await rpg.level2(ctx, mon, xp)
            else:
                await ctx.send(f"{user.mention} wins the drinking contest!")
                await rpg.level2(ctx, mon, xp, user)
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send("I guess they don't want to get drunk tonight.")
            ctx.command.reset_cooldown(ctx)
            return

    @drink.error
    async def drink_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"There is currently a drinking competition in {ctx.channel.mention}")

    @commands.group(invoke_without_command=True)
    async def guild(self, ctx):
        """Show your current guild."""

        async def msg():
            async with ctx.bot.db.acquire() as db:
                data = await db.fetchval("SELECT guild FROM profiles WHERE id=$1", ctx.author.id)
                if not data:
                    return f'{ctx.author.mention} You are not in a guild! To join a guild type `{ctx.prefix}guild join`'
                else:
                    return f'{ctx.author.mention} you are enlisted in {data}'
        await ctx.send(await msg())

    @guild.command(name="create", aliases=['form'])
    @checks.has_guild()
    async def _create_(self, ctx, *, name=None):
        """Create your own guild."""

        if not name:
            return await ctx.send("Provide a name!")

        await ctx.send(f"Are you sure you want to create a guild? This will cost $1000")
        user = await rpg.fetch_user2(ctx)
        yon = await rpg.yon(ctx)
        if yon == "Yes":
            if user[3] >= 10000:
                await ctx.send(f"You are now the leader and founder of {name}")
                async with ctx.bot.db.acquire() as db:
                    await db.execute("INSERT INTO guilds VALUES($1, $2, $3, $4)", name, ctx.author.id, 1, 0)
            else:
                return await ctx.send(f"{ctx.author.mention} You need ${10000 - user[3]} to create a guild!")
        else:
            return await ctx.send("I guess you don't want to create a guild")

    @guild.command()
    @checks.has_guild()
    async def join(self, ctx, *, name):
        """Join a guild."""

        async with ctx.bot.db.acquire() as db:
            leader = await db.fetchval("SELECT leader FROM guilds WHERE guild=$1", name)

        leader = self.bot.get_user(leader)
        await ctx.send(f"**{leader}** the leader of {name} has been informed of you application.")
        try:
            await leader.send(f"{leader.mention} Do you accept **{ctx.author}** into your guild? \n"
                              f"Yes or No?")
        except discord.Forbidden:
            await ctx.send(f"{leader.mention} Do you accept **{ctx.author}** into your guild? \n"
                           f"Yes or No?")

        def check(m):
            return m.author == leader and m.channel == leader and m.content.capitalize() in ["Yes", "No"]

        msg = (await ctx.bot.wait_for('message', check=check)).content.capitalize()
        if msg == "Yes":
            async with ctx.bot.db.acquire as db:
                await db.execute("UPDATE profiles SET guild=$1 WHERE id=$2", name, ctx.author.id)

            await ctx.send(f"{ctx.author.mention} you have been accepted to join {name}")
        else:
            return await ctx.send(f"{ctx.author.mention} you have been sadly rejected to join {name}")


Rpg2.__name__ = "Infamous RPG v2"


def setup(bot):
    bot.add_cog(Rpg2(bot))
