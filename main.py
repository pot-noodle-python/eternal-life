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
        
        print(f"loaded google sheet information:\n{self.values}")
    
    def save(self):
        if self.prev_values != self.values:
            print(f"saving values to google sheets:\n{self.values}")
            
            counts = []
            
            for key, value in self.values.items():
                counts.append([str(key), str(value)])
            
            self.sheet.update(f'A1:B{str(len(counts))}', counts)

            
            self.prev_values = self.values.copy()

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
            self.save()
            return True
        else:
            return False
    
    def load_count(self, id):
        print(f"loading user {id} locally")
        if self.values.get(str(id)):
            return self.values[str(id)]
        else:
            return "0"
    
    def load_total_count(self):
        print("loading total count locally")
        return str(sum([int(self.values[key]) for key, value in self.values.items()]))
    
    def check_count(self, id):
        return int(self.values[str(id)])

bot = commands.Bot(command_prefix='?')
database = Database()

keyword = "Humraj was a former member of the United States Special Forces, who was awarded the Medal of Honour for his actions in Vietnam, best known for surviving the impossible. He went to save his comrades who were outnumbered. The helicopter couldn't land because of the intense crossfire, so he jumped from the hovering helicopter around 30-50 feet in the air. He then had to run 75 metres to his comrades, where he was shot in the leg, face and head on the way. Once he got there, he started rescuing his squadmates and while he was doing so, got shot in the gut and took a grenade to the back. After all of this, he was miraculously still mobile and still going. Humraj then found out that the helicopter he previously jumped from had crashed so he went and rescued the wounded pilot from the wreckage and proceeded to call in airstrikes and call for another rescue attempt. He was shot in the thigh a couple more times and on his trip to the backup rescue chopper, he was beaten and stabbed by an enemy, who he then killed in hand to hand combat. Once he finally made it back to the chopper, he then allowed his comrades to pull him in. When they arrived back to the base, he was pronounced dead and put into a body bag. As they were zipping up the body bag, he had only the strength to spit to show he was still alive."
bot.bless_cooldown = 60
bot.commandd_cooldown = 5
bot.sin_cooldown = 90
lowercase_count = {}

@bot.event
async def on_ready():
    print('Logged on as', bot.user)

@bot.event
async def on_message(message):
    global lowercase_count

    if message.channel.id == 840636416656277576:
        if message.content.lower().translate(str.maketrans('', '', string.punctuation)) == keyword.lower().translate(str.maketrans('', '', string.punctuation)):
            if database.save_count(message.author.id):
                await message.author.add_roles(get(message.author.guild.roles, name="Priest"))
                await message.reply("**YOU HAVE NOW ASCENDED INTO A PRIEST BY PRAISING MASTER HUMRAJ 200 TIMES.**")
        elif "humraj" in message.content:
            count = random.randint(-8, -2)
            database.save_count(message.author.id, increment=count)
            if lowercase_count.get(str(message.author.id)):
                lowercase_count[str(message.author.id)] = str(int(lowercase_count[str(message.author.id)]) + 1)
            else:
                lowercase_count[str(message.author.id)] = "1"
            
            if lowercase_count[str(message.author.id)] == "3":
                print("yes")
                await message.author.add_roles(get(message.author.guild.roles, name="Sinners"))
            
            if lowercase_count[str(message.author.id)] == "10":
                await message.author.add_roles(get(message.author.guild.roles, name="Devil"))

            print(lowercase_count)
            await message.reply(f"{str(count).split('-')[1]} prayers have been deducted from you for spelling **Master Hurmaj's** name without an **uppercase letter**. I'd suggest confiding in a **Priest** and confessing your sins.")
            await asyncio.sleep(3)
            await message.delete()

    await bot.process_commands(message)

@bot.command()
async def command_list(ctx):
    embedVar = discord.Embed(title="Command List", description="**?count** - see how many times you have praised master Humraj\n\n**?total** - see how many times we have praised master Humraj, collectively\n\n**?bless <user mention/ID>** - if you know, you know\n\n**?steal <user mention/ID>** - commit some sins to perform this action...\n\n**?pickpocket <user mention/ID>** - theres no going back once you can do this...", color=0x00ff00)
    await ctx.send(embed=embedVar)

@bot.command()
@commands.has_role('Sinners')
@commands.cooldown(1, bot.sin_cooldown, commands.BucketType.user)
async def steal(ctx, user: User):
    count = random.randint(1, 10)

    if database.check_count(user.id) >= 200:
        database.save_count(user.id, increment=-1*count)
        database.save_count(ctx.message.author.id, increment=count)
        await ctx.message.reply(f"**{count}** prayers have been successfully stolen from {user.mention}. Humraj wouldn't be very proud but oh well...")
    else:
        await ctx.message.reply(f"Humraj doesn't want you stealing from the poor. **scum**.")


@bot.command()
@commands.has_role('Devil')
@commands.cooldown(1, bot.sin_cooldown*2, commands.BucketType.user)
async def pickpocket(ctx, user: User):
    count = random.randint(5, 15)

    if database.check_count(user.id) >= 250:
        database.save_count(user.id, increment=-1*count)
        database.save_count(ctx.message.author.id, increment=count)
        await ctx.message.reply(f"**{count}** prayers have been successfully pickpocketed from **{user.display_name}**. Humraj wouldn't be very proud but oh well...")
    else:
        await ctx.message.reply(f"Humraj doesn't want you stealing from the poor. **scum**.")

@bot.command()
@commands.cooldown(1, bot.commandd_cooldown, commands.BucketType.user)
async def count(ctx):
    count = database.load_count(ctx.message.author.id)
    await ctx.reply(f'You have made **{count}** prayers to master Humraj.')
    database.save()

@bot.command()
@commands.cooldown(1, bot.commandd_cooldown, commands.BucketType.user)
async def total(ctx):
    count = database.load_total_count()
    await ctx.reply(f"**{count}** prayers have been made to master Humraj, collectively.")
    database.save()

@bot.command()
@commands.has_role('Priest')
@commands.cooldown(1, bot.bless_cooldown, commands.BucketType.user)
async def bless(ctx, user: User):
    prayers = random.randint(10, 50)
    await ctx.message.reply(f"{user.mention} has been splashed with **{str(prayers)[0]} gallons of holy water** and **{prayers}** prayers have been made on their behalf.")
    if database.save_count(user.id, increment=prayers):
        await message.author.add_roles(get(message.author.guild.roles, name="Priest"))
        await ctx.send(f"**{user.mention} HAS NOW ASCENDED INTO A PRIEST BY PRAISING MASTER HUMRAJ 200 TIMES.**")

@bot.command()
@commands.has_role('Prophets')
async def set_bless_cooldown(ctx, cooldown):
    try:
        test = int(cooldown)
        bot.bless_cooldown = int(cooldown)
        await ctx.message.reply(f"cooldown between priest blessings has been set to {bot.bless_cooldown}s")
    except:
        await ctx.message.reply(f"{cooldown} is not a valid amount of seconds")

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


bot.run('ODQwMjU1MTE2OTYyODI0MjUy.YJVijw.P1BYNRl76j0WkvFTmplcjgnGV0w')