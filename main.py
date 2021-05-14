import string
import random
import asyncio

import discord
from discord import User
from discord.ext import commands
from discord.utils import get

import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Database:
    def __init__(self):
        self.values = {}
        self.prev_values = {}

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)

        self.sheet = client.open("Prayer Count").sheet1

        self.load()
    
    def load(self):
        list_of_hashes = self.sheet.get_all_values()
        
        for item in list_of_hashes:
            self.values[str(item[0])] = str(item[1])
        
        print(f"loaded google sheet information")
    
    def save(self):
        if self.prev_values != self.values:
            print(f"Detected change in values. Saving values to google sheets.")
            
            counts = []
            
            for key, value in self.values.items():
                counts.append([str(key), str(value)])
            
            self.sheet.update(f'A1:B{str(len(counts))}', counts)

            self.prev_values = self.values.copy()
        else:
            print(f"Save failed. No change detected in values.")

    def save_count(self, id, increment=1):
        print(f"updating user {id} locally")
        if self.values.get(str(id)):
            prayers_before = int(self.values[str(id)])
            self.values[str(id)] = str(int(self.values[str(id)]) + increment)
            prayers_after = int(self.values[str(id)])
        else:
            prayers_before = 0
            self.values[str(id)] = "1"
            prayers_after = 1
        
        if prayers_before < 200 and prayers_after >= 200:
            return 1
        elif prayers_before < 600 and prayers_after >= 600:
            return 2
        elif prayers_before < 1200 and prayers_after >= 1200:
            return 3
        else:
            return 0
    
    def load_count(self, id):
        print(f"loading user {id} locally")
        if self.values.get(str(id)):
            return self.values[str(id)]
        else:
            return "0"
    
    def load_total_count(self):
        print("loading total count locally")
        return str(sum([int(self.values[key]) for key, value in self.values.items()]))
    
    def leaderboard(self):
        print("loading leaderboard locally")
        return {k: v for k, v in sorted(self.values.items(), key=lambda item: int(item[1]), reverse=True)}


intents = discord.Intents().all()
bot = commands.Bot(command_prefix='?', intents=intents)
bot.remove_command('help')
database = Database()

keyword = "Humraj was a former member of the United States Special Forces, who was awarded the Medal of Honour for his actions in Vietnam, best known for surviving the impossible. He went to save his comrades who were outnumbered. The helicopter couldn't land because of the intense crossfire, so he jumped from the hovering helicopter around 30-50 feet in the air. He then had to run 75 metres to his comrades, where he was shot in the leg, face and head on the way. Once he got there, he started rescuing his squadmates and while he was doing so, got shot in the gut and took a grenade to the back. After all of this, he was miraculously still mobile and still going. Humraj then found out that the helicopter he previously jumped from had crashed so he went and rescued the wounded pilot from the wreckage and proceeded to call in airstrikes and call for another rescue attempt. He was shot in the thigh a couple more times and on his trip to the backup rescue chopper, he was beaten and stabbed by an enemy, who he then killed in hand to hand combat. Once he finally made it back to the chopper, he then allowed his comrades to pull him in. When they arrived back to the base, he was pronounced dead and put into a body bag. As they were zipping up the body bag, he had only the strength to spit to show he was still alive."
bot.bless_cooldown = 60
bot.commandd_cooldown = 5
bot.sin_cooldown = 90
bot.worship_channel = 840636416656277576
bot.lowercase_count = {}
bot.protect_count = {}

async def upgrade(result, message, user):
    priest_role = discord.utils.find(lambda r: r.name == 'Priest', message.guild.roles)
    bishop_role = discord.utils.find(lambda r: r.name == 'Bishop', message.guild.roles)
    archbishop_role = discord.utils.find(lambda r: r.name == 'Archbishop Of The Church Of Humraj', message.guild.roles)
    
    if result == 1 and priest_role not in user.roles:
        await user.add_roles(get(user.guild.roles, name="Priest"))
        await message.reply(f"**{user.mention} HAS NOW ASCENDED INTO A PRIEST BY PRAISING MASTER HUMRAJ 200 TIMES.**")
    elif result == 2 and bishop_role not in user.roles:
        await user.add_roles(get(user.guild.roles, name="Bishop"))
        await message.reply(f"**{user.mention} HAS NOW ASCENDED INTO A BISHOP BY PRAISING MASTER HUMRAJ 600 TIMES.**")
    elif result == 3 and archbishop_role not in user.roles:
        await user.add_roles(get(user.guild.roles, name="Archbishop Of The Church Of Humraj"))
        await message.reply(f"**{user.mention} HAS NOW ASCENDED INTO AN ARCHBISHOP BY PRAISING MASTER HUMRAJ 1200 TIMES.**")

async def time_save():
    while True:
        await asyncio.sleep(10)
        database.save()

@bot.event
async def on_ready():
    bot.loop.create_task(time_save())
    print('Logged on as', bot.user)

@bot.event
async def on_message(message):

    if message.channel.id == bot.worship_channel:
        if message.content.lower().translate(str.maketrans('', '', string.punctuation)) == keyword.lower().translate(str.maketrans('', '', string.punctuation)):
            result = database.save_count(message.author.id)

            await upgrade(result, message, message.author)
        elif "humraj" in message.content:
            count = random.randint(-8, -2)

            sin_role = discord.utils.find(lambda r: r.name == 'Sinners', message.guild.roles)
            devil_role = discord.utils.find(lambda r: r.name == 'Devils', message.guild.roles)
            
            if bot.lowercase_count.get(str(message.author.id)):
                bot.lowercase_count[str(message.author.id)] = str(int(bot.lowercase_count[str(message.author.id)]) + 1)
            else:
                bot.lowercase_count[str(message.author.id)] = "1"
            
            if sin_role not in message.author.roles:
                if bot.lowercase_count[str(message.author.id)] == "3":
                    await message.author.send("**check your roles... 😈**")
                    await message.author.add_roles(get(message.author.guild.roles, name="Sinners"))

            if devil_role not in message.author.roles:
                if bot.lowercase_count[str(message.author.id)] == "10":
                    await message.author.send("**check your roles... 👿**")
                    await message.author.add_roles(get(message.author.guild.roles, name="Devil"))

            if sin_role in message.author.roles:
                await message.reply(f"{str(count).split('-')[1]} prayers have been deducted from you for spelling **Master Humraj's** name without an **uppercase letter**. I'd suggest confiding in a **Priest** and confessing your sins.")
            else:
                await message.reply(f"{str(count).split('-')[1]} prayers have been deducted from you for spelling **Master Humraj's** name without an **uppercase letter**. I'd suggest confiding in a **Priest** and confessing your sins.\n\n**almost there 😈 ...**")
            
            database.save_count(message.author.id, increment=count)

            await asyncio.sleep(3)
            await message.delete()
    else:
        correct_channel = bot.get_channel(bot.worship_channel)
        if message.content.lower().translate(str.maketrans('', '', string.punctuation)) == keyword.lower().translate(str.maketrans('', '', string.punctuation)):
            bot_msg = await message.reply(f"Don't praise **Humraj** here. Worship in {correct_channel.mention} instead.")

            await message.delete()
            await asyncio.sleep(3)
            await bot_msg.delete()

    await bot.process_commands(message)

@bot.command()
async def help(ctx):
    embedVar = discord.Embed(title="Command List", description="""
    **?count** - see how many times you have praised master Humraj\n\n
    **?total** - see how many times we have praised master Humraj, collectively\n\n
    **?bless <user mention/ID>** - if you know, you know\n\n
    **?protect <user mention/ID>** protect people from sins\n\n
    **?baptize <user mention/ID>** - shower someone in holy water\n\n
    **?steal <user mention/ID>** - commit some sins to perform this action...\n\n
    **?pickpocket <user mention/ID>** - theres no going back once you can do this...\n\n
    **?leaderboard** - return a leaderboard of prayers.
    """, color=0x00ff00)

    await ctx.send(embed=embedVar)
    embedVar = discord.Embed(title="How to praise Humraj:", description="**Type the following in chat:**\n\nHumraj was a former member of the United States Special Forces, who was awarded the Medal of Honour for his actions in Vietnam, best known for surviving the impossible. He went to save his comrades who were outnumbered. The helicopter couldn't land because of the intense crossfire, so he jumped from the hovering helicopter around 30-50 feet in the air. He then had to run 75 metres to his comrades, where he was shot in the leg, face and head on the way. Once he got there, he started rescuing his squadmates and while he was doing so, got shot in the gut and took a grenade to the back. After all of this, he was miraculously still mobile and still going. Humraj then found out that the helicopter he previously jumped from had crashed so he went and rescued the wounded pilot from the wreckage and proceeded to call in airstrikes and call for another rescue attempt. He was shot in the thigh a couple more times and on his trip to the backup rescue chopper, he was beaten and stabbed by an enemy, who he then killed in hand to hand combat. Once he finally made it back to the chopper, he then allowed his comrades to pull him in. When they arrived back to the base, he was pronounced dead and put into a body bag. As they were zipping up the body bag, he had only the strength to spit to show he was still alive.", color=0x00ff00)
    await ctx.send(embed=embedVar)

@bot.command()
@commands.has_permissions(administrator=True)
async def save(ctx):
    database.save()
    await ctx.message.reply("saved values to google sheets. Don't spam this command")

@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx):
    database.load()
    await ctx.message.reply("loaded values from google sheets. Don't spam this command")

@bot.command()
@commands.has_permissions(administrator=True)
async def add_prayers(ctx, count, user: User):
    database.save_count(user.id, increment=int(count))
    await ctx.reply(f"added {count} prayers to {user.id}")

@bot.command()
@commands.has_permissions(administrator=True)
async def remove_prayers(ctx, count, user: User):
    database.save_count(user.id, increment=-1*int(count))
    await ctx.reply(f"removed {count} prayers from {user.id}")

@bot.command()
@commands.has_role('Bishop')
@commands.cooldown(1, 1200, commands.BucketType.user)
async def protect(ctx, user: User):

    if user == ctx.message.author:
        await ctx.message.reply("**Master Humraj** says you can't protect yourself, that's something a **devil** would do.")
        return
    
    bot.protect_count[str(user.id)] = random.randint(5, 10)

    await ctx.message.reply(f"You have successfully cast a spell on {user.mention} and have protected them **temporarily**")

@bot.command()
@commands.cooldown(1, bot.commandd_cooldown, commands.BucketType.user)
async def leaderboard(ctx):
    leaderboard = database.leaderboard()

    await bot.wait_until_ready()

    embed = discord.Embed(title="Leaderboard", description="List of top worshippers", color=0x00ff00)
    i = 0
    for user, count in leaderboard.items():

        mention = bot.get_user(int(user))

        if mention is None:
            continue

        i += 1
        
        if i == 11:
            break

        embed.add_field(name=f"{i}. {mention.display_name}", value=f"Prayers: {count}", inline=False)
    
    embed.add_field(name="...", value="\u200b", inline=False)
    embed.set_footer(text=f"You are position {list(leaderboard).index(str(ctx.message.author.id)) + 1} on the leaderboard and you have {database.load_count(ctx.message.author.id)} prayers")

    await ctx.reply(embed=embed)

@bot.command()
@commands.has_role('Sinners')
@commands.cooldown(1, bot.sin_cooldown, commands.BucketType.user)
async def steal(ctx, user: User):

    count = random.randint(1, 10)

    if int(database.load_count(user.id)) >= 200:
        if not bot.protect_count.get(str(user.id)):
            database.save_count(user.id, increment=-1*count)
            database.save_count(ctx.message.author.id, increment=count)
            await ctx.message.reply(f"**{count}** prayers have been successfully stolen from {user.mention}. Humraj wouldn't be very proud but oh well...")
        else:
            await ctx.message.reply(f"{user.mention} is currently being protected by a **bishop** ")
            bot.protect_count[str(user.id)] -= 1
            if bot.protect_count[str(user.id)] == 0:
                del bot.protect_count[str(user.id)]
    else:
        await ctx.message.reply(f"Humraj doesn't want you stealing from the poor. **scum**.")


@bot.command()
@commands.has_role('Devil')
@commands.cooldown(1, bot.sin_cooldown*2, commands.BucketType.user)
async def pickpocket(ctx, user: User):
    count = random.randint(5, 15)

    if int(database.load_count(user.id)) >= 250:
        if not bot.protect_count.get(str(user.id)):
            database.save_count(user.id, increment=-1*count)
            database.save_count(ctx.message.author.id, increment=count)
            await ctx.message.reply(f"**{count}** prayers have been successfully pickpocketed from **{user.display_name}**. Humraj wouldn't be very proud but oh well...")
        else:
            await ctx.message.reply(f"{user.mention} is currently being protected by a **bishop** ")
            bot.protect_count[str(user.id)] -= 1
            if bot.protect_count[str(user.id)] == 0:
                del bot.protect_count[str(user.id)]
            
            if random.randint(1, 2) == 1:
                await ctx.message.author.send(f"Don't tell anyone I told you this but **{user.display_name}** is only protected for the next {bot.protect_count[str(user.id)]} sins.")
    else:
        await ctx.message.reply(f"Humraj doesn't want you stealing from the poor. **scum**.")

@bot.command()
@commands.cooldown(1, bot.commandd_cooldown, commands.BucketType.user)
async def count(ctx):
    count = database.load_count(ctx.message.author.id)
    await ctx.reply(f'You have made **{count}** prayers to master Humraj.')

@bot.command()
@commands.cooldown(1, bot.commandd_cooldown, commands.BucketType.user)
async def total(ctx):
    count = database.load_total_count()
    await ctx.reply(f"**{count}** prayers have been made to master Humraj, collectively.")

@bot.command()
@commands.has_role('Priest')
@commands.cooldown(1, bot.bless_cooldown, commands.BucketType.user)
async def bless(ctx, user: User):
    if user == ctx.message.author:
        await ctx.message.reply("**Master Humraj** says you can't bless yourself, that's unholy.")
        return
    
    prayers = random.randint(10, 50)
    await ctx.message.reply(f"{user.mention} has been splashed with **{str(prayers)[0]} gallons of holy water** and **{prayers}** prayers have been made on their behalf.")
    result = database.save_count(user.id, increment=prayers)
    await upgrade(result, ctx.message, user)

#Error handling
@bless.error
async def bless_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.reply(f"**Master Humraj** says you have to wait **{error.retry_after:.2f}**s before you bless someone again")
    if isinstance(error, commands.CheckFailure):
        await ctx.message.reply(f"**Master Humraj** says you have to praise him more before you can become a **Priest** and bless someone. **Get to work.**")

@total.error
async def total_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.reply(f"**Master Humraj** says you can only use this command once every 5 seconds")

@count.error
async def count_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.reply(f"**Master Humraj** says you can only use this command once every 5 seconds")

@leaderboard.error
async def leaderboard_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.reply(f"**Master Humraj** says you can only use this command once every 5 seconds")

@steal.error
async def steal_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.reply(f"Stealing is tiring work. **Sinners** can't be working all night.")
    if isinstance(error, commands.CheckFailure):
        await ctx.message.reply(f"**Master Humraj** says you don't look like much of a **sinner** at all. Get back to praying!")

@pickpocket.error
async def pickpocket_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.reply(f"Stealing is tiring work. **Devils** can't be working all night.")
    if isinstance(error, commands.CheckFailure):
        await ctx.message.reply(f"**Master Humraj** says you don't look like much of a **devil** at all. Get back to praying!")

@protect.error
async def protect_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.reply("**Humraj** says you can only protect someone once every 20 minutes. Get back to praying.")
    if isinstance(error, commands.CheckFailure):
        await ctx.message.reply(f"**Master Humraj** says you're not holy enough to be protecting people. **Pray more peasant!**")


bot.run('ODQwMjU1MTE2OTYyODI0MjUy.YJVijw.O8GfshvfH9ZASX8AvDTSvfEuCXw')