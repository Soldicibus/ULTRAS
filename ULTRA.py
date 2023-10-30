import disnake
from disnake.ext import commands
from disnake.ext.commands import bot
from disnake.utils import get
import config
import asyncio
import time
from roles import sqlite3
import roles
from time import strftime
from time import localtime


def get_user_data():
    conn = sqlite3.connect('leveling.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, level, experience FROM users')
    user_data = cursor.fetchall()
    conn.close()
    return user_data

def check_user_experience():
    user_data = get_user_data()
    for user_id, username, level, experience in user_data:
        if experience >= 5 * level:
            level += 1
            update_user_level(user_id, level)
            print ('Новий рівень користувача')
            
def update_user_level(user_id, new_level):
    conn = sqlite3.connect('leveling.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET level = ? WHERE user_id = ?', (new_level, user_id))
    conn.commit()
    conn.close()

bot = commands.Bot(command_prefix=config.PREFIX, help_command=None, intents=disnake.Intents.all())

@bot.event
async def on_ready():
    await bot.change_presence(status=disnake.Status.dnd, activity=disnake.Game(name=".help", type=2))
    print("[!] Logged in as:")
    print("[!] Status: ✅")
    print("[!] The bot is ready to work")
    check_user_experience()

@bot.event
async def on_message(message):
    check_user_experience()
    await bot.process_commands(message)

    msg = message.content.lower()
    censored_words = config.PROHIBITED_WORDS

    for bad_content in msg.split():
        if bad_content in censored_words:
            await message.delete()
            await message.channel.send(f"{message.author.mention}**, ай-ай-ай... Плохо, плохо, так нельзя!**")

@bot.event
async def on_raw_reaction_add(payload):
    post_id = config.MESSAGE_ID
    role_id = config.ID_ROLE

    role_name = "Участник👀"
    message_id = payload.message_id
    author = payload.member
    if(message_id == post_id):
        role = disnake.utils.get(payload.member.guild.roles, id=config.ID_ROLE)
        await author.add_roles(role)
        print(format(payload.member) + ' got the role:' + '\''+role_name+'\'!')

@bot.event
async def on_command_error(ctx, error):
    print(error)

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"**{ctx.author}, у вас недостатньо прав для виконання цієї команди!**")
    elif isinstance(error, commands.UserInputError):
        await ctx.send(embed=disnake.Embed(
            description=f"**Правильне використання команди: `{ctx.prefix}{ctx.command.name}` ({ctx.command.brief})\nExample: {ctx.prefix}{ctx.command.usage}**"
        ))
       
        #проверка на модератора
def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

@bot.command(name="ранк", aliases=["rank", "rk"], brief="Перевірити свій рівень", usage="rank")
async def rank(ctx):
    user_id = ctx.author.id
    user = roles.get_user(user_id)
    
    if user:
        roles.update_user_exp(user_id)
    else:
        roles.add_user(user_id, ctx.author.name)
        
    user_id = ctx.author.id
    user = roles.get_user(user_id)

    emb = disnake.Embed(color=344462)
    emb.add_field(name="Користувач", value=user[1], inline = False)
    emb.add_field(name="Рівень:", value = user[2], inline = False)
    emb.add_field(name="Досвід:", value = user[3], inline = False)
    await ctx.send(embed = emb)

@bot.command(name="рейтинг", aliases=["rating", "rate"], brief="Рейтинг користувачів ботом", usage="rating")
async def ratings(ctx):
    user_id = ctx.author.id
    user = roles.get_user(user_id)
    
    if user:
        roles.update_user_exp(user_id)
    else:
        roles.add_user(user_id, ctx.author.name)
        
    conn = sqlite3.connect('leveling.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, level, experience FROM users')
    user_data = cursor.fetchall()

    sorted_users = sorted(user_data, key=lambda x: (x[2], x[3]), reverse=True)

    rating_message = "Топ користувачів:\n"
    for i, (user_id, username, level, experience) in enumerate(sorted_users, start=1):
        rating_message += f"{i}. {username}: Рівень {level}, Досвід {experience}\n"
    await ctx.send(rating_message)

    conn.close()


@bot.command(name="Перевірити", aliases=["chek"], brief="Перевірити на модератора", usage="check")
@commands.check_any(commands.is_owner(), is_guild_owner())
async def chek(ctx):
    user_id = ctx.author.id
    user = roles.get_user(user_id)
    
    if user:
        roles.update_user_exp(user_id)
    else:
        roles.add_user(user_id, ctx.author.name)
    guild = str(ctx.guild)
    await ctx.author.send(f'**{ctx.guild}**: Ви модератор!')
    await ctx.send(f'**{ctx.guild}**: Ви модератор!')
    #############################
@bot.command()
async def whereami(ctx):
   await ctx.send(f'You are on {ctx.guild} on {ctx.channel}')

@bot.command()
@commands.has_permissions(administrator=True, manage_messages=True)
async def say(ctx, * , arg):
    user_id = ctx.author.id
    user = roles.get_user(user_id)
    
    if user:
        roles.update_user_exp(user_id)
    else:
        roles.add_user(user_id, ctx.author.name)
    emb = disnake.Embed(title = f'**{ctx.guild}**\n' + arg, color=000000)
    await ctx.message.delete()
    await ctx.send(embed=emb)

@bot.command(name="мут", aliases=["mute", "mute-member"], brief="Заборонити користувачеві надсилати повідомлення.", usage="mute <member> <time> <reason>")
@commands.has_permissions(administrator=True,manage_roles=True)
async def mute(ctx, member: disnake.Member, mute_time: int, reason):
    user_id = ctx.author.id
    user = roles.get_user(user_id)
    
    if user:
        roles.update_user_exp(user_id)
    else:
        roles.add_user(user_id, ctx.author.name)
    mute_role = disnake.utils.get(ctx.message.guild.roles, id=config.MUTE_ROLE_ID)
    emb = disnake.Embed(color=344462)
    emb.add_field(name="✅ Muted", value='Коричтувач {} був замьючен!'.format(member.mention))
    emb.add_field(name="Модератор", value = ctx.message.author.mention, inline = False)
    emb.add_field(name="Причина", value = reason, inline = False)
    emb.add_field(name="Час", value = mute_time, inline = False)
    await ctx.send(embed = emb)
    await ctx.author.send(f'**{ctx.guild}**: Вас замутили!')
    await member.add_roles(mute_role)
    await asyncio.sleep(mute_time * 60)
    await member.remove_roles(mute_role)

#размут
@bot.command()
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: disnake.Member):
    user_id = ctx.author.id
    user = roles.get_user(user_id)
    
    if user:
        roles.update_user_exp(user_id)
    else:
        roles.add_user(user_id, ctx.author.name)
    mute_role = disnake.utils.get(member.guild.roles, id=config.MUTE_ROLE_ID)
    emb = disnake.Embed(color=344462)
    emb.add_field(name="✅ UnMuted", value='Користувач {} був размьючен!'.format(member.mention))
    emb.add_field(name="Модератор", value = ctx.message.author.mention, inline = False)
    await ctx.send(embed = emb)
    await ctx.author.send(f'**{ctx.guild}**: Вас розмутили!')
    await member.remove_roles(mute_role)

@bot.command(name="очистити", aliases=["clear", "cl"], brief="Очистити чат від повідомлень", usage="clear <amount=10>")
@commands.has_permissions(administrator=True, manage_messages=True)
async def clear(ctx, amount: int=10):
    user_id = ctx.author.id
    user = roles.get_user(user_id)
    
    if user:
        roles.update_user_exp(user_id)
    else:
        roles.add_user(user_id, ctx.author.name)
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"**{ctx.guild}**:Було видалено {amount + 1} повідомлень.", delete_after=3)

@bot.command(name="кик", aliases=["kick", "kick-member"], brief="Вигнати користувача із сервера", usage="kick <@user> <reason=None>")
@commands.has_permissions(administrator=True, kick_members=True)
async def kick(ctx, member: disnake.Member, *, reason=None):
    user_id = ctx.author.id
    user = roles.get_user(user_id)
    
    if user:
        roles.update_user_exp(user_id)
    else:
        roles.add_user(user_id, ctx.author.name)
    await ctx.message.delete()
    await ctx.send(f"**{ctx.guild}**: Користувач {member.mention}, був вигнаний із сервера!", delete_after=3)
    await ctx.author.send(f'**{ctx.guild}**: Вас кікнули!')
    await member.kick(reason=reason)

@bot.command(name="бан", aliases=["ban", "ban-member"], brief="Забанити користувача на сервері", usage="ban <@user> <reason=None>")
@commands.has_permissions(administrator=True, ban_members=True)
async def ban(ctx, member: disnake.Member, *, reason=None):
    user_id = ctx.author.id
    user = roles.get_user(user_id)
    
    if user:
        roles.update_user_exp(user_id)
    else:
        roles.add_user(user_id, ctx.author.name)
    await ctx.message.delete()
    await ctx.send(f"**{ctx.guild}**: Користувач {member.mention}, був забанен на сервері.")
    await ctx.author.send(f'**{ctx.guild}**: Вас забанили!')
    await member.ban(reason=reason)

@bot.command(name="разбанить", aliases=["unban", "unban-member"], brief="Розбанити користувача на сервері", usage="unban <user_id>")
@commands.has_permissions(administrator=True, ban_members=True)
async def unban(ctx, user_id: int):
    user_id = ctx.author.id
    user = roles.get_user(user_id)
    
    if user:
        roles.update_user_exp(user_id)
    else:
        roles.add_user(user_id, ctx.author.name)
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"**{ctx.guild}**: Користувач розбанений")
    await ctx.author.send(f'**{ctx.guild}**: Вас розбанили!')

@bot.command()
async def join(msg):
    try:
        voice_client = await msg.author.voice.channel.connect()
    except:
        print("error")
        
@bot.command()
async def help( ctx ):
        emb = disnake.Embed( title = f'✅ Информація о командах сервера **{ctx.guild}**', color=344462)
        emb.add_field( name = '{}clear'.format( config.PREFIX ), value = 'Розбанити користувача на сервері', inline = False)
        emb.add_field( name = '{}kick'.format( config.PREFIX ), value = 'Кік участника сервера', inline = False)
        emb.add_field( name = '{}mute'.format( config.PREFIX ), value = 'Видати мут учаснику сервера', inline = False)
        emb.add_field( name = '{}unmute'.format( config.PREFIX ), value = 'Зняття мута на сервері', inline = False)
        emb.add_field( name = '{}chek'.format( config.PREFIX ), value = 'Перевірка прав модератора', inline = False)
        emb.add_field( name = '{}ban'.format( config.PREFIX ), value = 'Бан користувача на сервері')
        emb.add_field( name = '{}say'.format( config.PREFIX ), value = 'Дублювання вашого повідомлення', inline = False)
        emb.set_thumbnail(ctx.author.avatar)
        emb.add_field( name = '{}info'.format( config.PREFIX ), value = 'Показати детальну інформацію про користувача', inline = False)
        await ctx.author.send(embed = emb)
        await ctx.send(f'**{ctx.guild}**: *****Надіслав вам список команд на личку :D*****')

bot.run(config.TOKEN)
