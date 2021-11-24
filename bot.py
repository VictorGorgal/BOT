from sideprograms.tic_tac_toe import TicTacToe
from sideprograms.Japanese import japanese
from sideprograms.img2ascii import img2ascii
from sideprograms.logger import logger
from sideprograms.YTDL import YTDLSource
from discord.ext import commands
from discord.utils import get
from youtube_search import YoutubeSearch
from datetime import datetime
from difflib import SequenceMatcher
from operator import itemgetter
from serial import Serial
import youtube_dl
import sideprograms.rpg_classes as rpg
import numpy as np
import pypresence
import time
import cv2
import functools
import gtts
import discord
import random
import os
import json
import shelve
import bs4
import requests
import asyncio
import asyncpraw
import weathercom


class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents, self_bot):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents, self_bot=self_bot)
        self.MORSE_CODE_DICT = {'A': '.-', 'B': '-...',
                                'C': '-.-.', 'D': '-..', 'E': '.',
                                'F': '..-.', 'G': '--.', 'H': '....',
                                'I': '..', 'J': '.---', 'K': '-.-',
                                'L': '.-..', 'M': '--', 'N': '-.',
                                'O': '---', 'P': '.--.', 'Q': '--.-',
                                'R': '.-.', 'S': '...', 'T': '-',
                                'U': '..-', 'V': '...-', 'W': '.--',
                                'X': '-..-', 'Y': '-.--', 'Z': '--..',
                                '1': '.----', '2': '..---', '3': '...--',
                                '4': '....-', '5': '.....', '6': '-....',
                                '7': '--...', '8': '---..', '9': '----.',
                                '0': '-----', ', ': '--..--', '': '',
                                '?': '..--..', '/': '-..-.',
                                '(': '-.--.', ')': '-.--.-'}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}
        self.fight_dict = {}
        self.queue = {}
        self.music = {}
        self.searching = {}
        self.music_message = {}
        self.P = command_prefix
        self.voice = None
        self.casando_p = None
        self.casando_u = None
        self.battle = None
        self.tic = None
        self.jap = None
        self.joining_member = None
        self.paused = False
        self.casando = False
        self.rpg = False
        self.tic_tac_toe = False
        self.hiragana = False
        self.katakana = False
        self.fight = False
        self.playing = False
        self.PALAVRAS_PROIBIDAS = []
        self.vids = []
        self.banned = []
        self.channel_banned = []
        self.track = []
        self.volume = 0.16
        self.fds_chance = 0.2  # %
        self.slave_id = 757795510357590148
        self.master_id = 000  # credencial
        self.path = os.path.realpath(__file__).replace('\\bot.py', '')
        self.logger = logger(self.path)
        self.reddit = asyncpraw.Reddit(client_id='xxx',  # credencial
                                       client_secret='xxx',
                                       user_agent='xxx')
        self.remove_command('help')
        self.remove_old_songs()
        self.add_commands()

    async def on_ready(self):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{self.P}help"))
        with shelve.open(f'{self.path}/database/music/music') as music:
            self.music = dict(music)
        with shelve.open(f'{self.path}/database/music/music_message') as msg:
            self.music_message = dict(msg)
        # self.usb_task = threading.Thread(target=usb)
        # self.usb_task.start()

        self.discount_task = self.loop.create_task(self.discount())

        if shelve.open(f'{self.path}/database/hinos/hinos'):
            self.anthem_task = self.loop.create_task(self.anthem())

        self.anime_task = self.loop.create_task(self.anime())

        # self.crackwatch_task = self.loop.create_task(self.crackwatch())

        # self.starweb_task = self.loop.create_task(self.starweb())

        print("Bot ready!")

        dir_to_flush = f'{self.path}/music/queue'  # flushing song queue at start up... (obsolete)
        files = os.listdir(dir_to_flush)
        if len(files) > 0:
            for file in files:
                os.remove(f'{dir_to_flush}/{file}')
        if os.path.isfile('output.mp3'):
            os.remove('output.mp3')

    def add_commands(self):
        @self.before_invoke  # run before every command
        async def common(message):
            if message.author.id in self.banned:  # if user is banned, exit command
                raise user_banned
            if random.randint(1,
                              int(1 / (self.fds_chance / 100))) == 1:  # chance for the bot to rebel against user (joke)
                print(f'{message.author.nick} rolou o {self.fds_chance}%')
                await message.channel.send('Tu eh chato pqp, quer sbr, desisto vlw flw troxa')
                self.banned.append(message.author.id)
                raise user_banned

        @self.event
        async def on_message(message):
            await bot.process_commands(message)
            self.logger.log_message(message)
            guild = message.guild
            channel = message.channel
            content = message.content

            for palavra in self.PALAVRAS_PROIBIDAS:  # deletes comments with banned words
                if palavra in content:
                    await message.delete()
                    await channel.send("Nao pode fala isso, eh feio")

            if guild.id in self.searching and self.searching[guild.id]:
                if message.author.id != self.slave_id and f'{self.P}play' not in content:  # music choice algorithm
                    try:
                        escolha = int(content)
                        ctx = self.vids[0][0]
                        if channel.id == ctx.channel.id:
                            self.searching[guild.id] = False
                            if escolha in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                                url = self.vids[escolha][1]
                                print(url)
                                ctx.content = url
                                await self.vids[0][1].delete()
                                await message.delete()
                                self.vids.clear()
                                await play(ctx)
                            elif escolha == 0:
                                await self.vids[0][1].delete()
                                await message.delete()
                                self.vids.clear()

                    except ValueError:
                        pass
            else:
                if self.slave_id != message.author.id and not content.startswith(self.P):
                    if str(guild.id) in self.music and channel.id == self.music[str(guild.id)]:
                        for v_channel in guild.voice_channels:
                            for member in v_channel.members:
                                if member == message.author:
                                    await join(message, v_channel)
                        await play(message)

            if self.tic_tac_toe:  # tic tac toe algorithm
                if self.tic.running:
                    if self.tic.playing(message.author.name) and self.tic.valid_inputs(content):
                        played = list(content.upper().replace("Q", "1").replace("W", "2").replace("E", "3"))
                        self.tic.x = int(played[1]) - 1
                        self.tic.y = int(played[0]) - 1
                        if self.tic.game[self.tic.y][self.tic.x] == " - ":
                            self.tic.game[self.tic.y][self.tic.x] = " X " if self.tic.player1 else " O "
                            self.tic.player1 = not self.tic.player1
                            temp_message = f'Vez do {self.tic.get_playing_name()}\n'
                            temp_message += self.tic.draw(emojy=True)
                            await self.tic.message.edit(content=temp_message)
                        else:
                            temp_message = f"o lugar {content.upper()} ja foi marcado!\n"
                            temp_message += self.tic.draw(emojy=True)
                            await self.tic.message.edit(content=temp_message)
                        if self.tic.check() is not None:
                            await channel.send(self.tic.check())
                        await message.delete()

            if (self.hiragana or self.katakana) and message.author.id != self.slave_id:  # hira or kana algorithm
                channel_jap = bot.get_channel(self.jap.channel_id)
                if channel.id == self.jap.channel_id and not content.lower() == 'para':
                    if self.jap.last_answer:
                        await channel_jap.send(self.jap.check_answer(content))

                    if self.hiragana:
                        await channel_jap.send(f'Hiragana: {self.jap.random_hiragana()}')
                    else:
                        await channel_jap.send(f'Katakana: {self.jap.random_katakana()}')
                else:
                    if content.lower() == 'para':
                        await channel_jap.send('tabom')
                    await channel_jap.send(f'stats:\n{self.jap.stats()}')
                    self.hiragana = False
                    self.katakana = False

            if content.lower() == 'good bot':  # bot voting (up)
                good_bot = shelve.open(f'{self.path}/database/counter/counter')
                if 'good_bot' not in list(good_bot.keys()):
                    good_bot['good_bot'] = 0
                good_bot['good_bot'] += 1
                await channel.send(f"fui um bom garoto {good_bot['good_bot']} vezes")
                good_bot.close()

            if content.lower() == 'bad bot':  # bot voting (down)
                bad_bot = shelve.open(f'{self.path}/database/counter/counter')
                if 'bad_bot' not in list(bad_bot.keys()):
                    bad_bot['bad_bot'] = 0
                bad_bot['bad_bot'] += 1
                await channel.send(f"fui um pessimo garoto {bad_bot['bad_bot']} vezes")
                bad_bot.close()

            if 'yuri' in content.lower() and 'pizza' in content.lower():  # how many times yuri eated pizza (joke)
                with shelve.open(f'{self.path}/database/counter/counter') as pizza:
                    if 'yuri_pizza_counter' not in list(pizza.keys()):
                        pizza['yuri_pizza_counter'] = 5
                    pizza['yuri_pizza_counter'] += 1
                    await channel.send(f"PQP JA EH A {pizza['yuri_pizza_counter']}º VEZ Q TU TA COMENDO PIZZA")

            if 'flip' in content.lower() and 'miojo' in content.lower():  # how many times flip eated miojo (joke)
                with shelve.open(f'{self.path}/database/counter/counter') as miojo:
                    if 'flip_miojo_counter' not in list(miojo.keys()):
                        miojo['flip_miojo_counter'] = 1
                    miojo['flip_miojo_counter'] += 1
                    await channel.send(f"PQP JA EH A {miojo['flip_miojo_counter']}º VEZ Q TU TA COMENDO MIJO")

            if self.fight and content.lower() == 'eu' and message.author.nick not in list(self.fight_dict.keys()):
                self.fight_dict[message.author.nick] = random.randint(1, 100)

            if content.lower().startswith('good ') or content.lower().startswith(  # voting other members (up or down)
                    'bad ') and message.author.id != self.slave_id:
                threshold = 0.6
                members = message.guild.members
                members_name = [member.name for member in members]
                ratio, mem = list_similar(content.split(' ')[1], members_name, anime_b=True)
                if ratio > threshold:
                    for member in members:
                        if member.name == mem:
                            rank = shelve.open(f'{self.path}/database/rank/rank')
                            mem_id = str(member.id)
                            if str(member.id) not in list(rank.keys()):
                                rank[mem_id] = 0
                            mensage = content.lower()
                            if mensage.startswith('good '):
                                rank[mem_id] += 1
                                await channel.send(f'{member.nick} + 1')
                            else:
                                rank[mem_id] -= 1
                                await channel.send(f'{member.nick} - 1')
                            rank.close()

            if 'quero comer terra' in content.lower():  # Making fun of Bradesco's artificial inteligence (joke)
                await channel.send(
                    'O que pra voce pode ter sido so uma brincadeira ou um comentario, pra mim foi violento.\n\n'
                    'Sou uma inteligencia artificial, mas imagino como essas palavras sao desrespeitosas e invasivas para mulheres reais.\n\n'
                    'Nao fale assim comigo e com mais ninguem')

        @self.event
        async def on_raw_reaction_add(message):
            # self.logger.log_reaction(message)
            emoji = message.emoji.name
            guild_id = message.guild_id
            member = message.member

            if str(guild_id) in self.music_message:
                if message.message_id == self.music_message[str(guild_id)] and member.id != self.slave_id:
                    channel = bot.get_channel(message.channel_id)
                    msg = await channel.fetch_message(message.message_id)
                    await msg.remove_reaction(emoji, member)

                    guild = self.get_guild(guild_id)
                    if emoji == '⏯':
                        print(f'{member} play/paused the music')
                        for v_channel in guild.voice_channels:
                            if member in list(v_channel.members):
                                if self.paused:
                                    await resume(None, guild)
                                else:
                                    await pause(None, guild)
                                self.paused = not self.paused
                    elif emoji == '⏹':
                        print(f'{member} stoped the music')
                        await stop(None, guild)
                        embed = discord.Embed(title='Controller', description=f'Currently not playing...\n\n'
                                                                              f'Send a link to play',
                                              color=discord.Color.red())
                        embed.set_thumbnail(
                            url='https://64.media.tumblr.com/2b4fd10ad6a54af25605a764775943ae/tumblr_pndzvk9ESR1xn70plo1_400.jpg')

                        msg_id = int(self.music_message[str(guild_id)])
                        msg = await channel.fetch_message(msg_id)
                        await msg.edit(embed=embed)
                    elif emoji == '⏭':
                        print(f'{member} skipped the music')
                        await skip(None, guild)

            if self.casando and message.member == self.casando_u:  # virtual wedding (why? idk, bored I guess)
                channel = bot.get_channel(message.channel_id)
                if emoji == '💘':
                    await channel.send(
                        f"{self.casando_u.name} e {self.casando_p.name} agr estao casados, se houver traicao eu vo mata os 2")
                    casados = shelve.open(f'{self.path}/database/casados/casados')
                    casados[self.casando_p.name] = self.casando_u.name
                    casados[self.casando_u.name] = self.casando_p.name
                    casados.close()
                else:
                    await channel.send(
                        f"foi mal {self.casando_p.name}, tua amada te odeia cara mas pelo lado bom n eh so ela q te odeia, eu tbm te odeio")

                self.casando = False

            if self.rpg and member.id == self.battle.player.user_id and message.message_id == self.battle.bot_mes.id:  # RPG game algorithm
                if member.id != self.slave_id:
                    channel = self.battle.player.channel
                    if not self.battle.won():
                        self.battle.bot_mes = await channel.send(self.battle.attack(emoji))
                        for e in self.battle.to_add():
                            await self.battle.bot_mes.add_reaction(e)
                        if self.battle.dead():
                            await channel.send('Perdeu bbk')
                            self.rpg = False
                            self.battle = None
                            return

                    if self.battle.won():
                        if self.battle.Tafter_killing:
                            self.battle.bot_mes = await channel.send(self.battle.after_killing())
                            await self.battle.bot_mes.add_reaction('🇸')
                            await self.battle.bot_mes.add_reaction('🇳')
                        elif self.battle.Tequip:
                            self.battle.equip(emoji)
                        else:
                            self.battle.Tequip = False

                        if not self.battle.Tequip:
                            if self.battle.Tlevelup_message and self.battle.level_check():
                                self.battle.bot_mes = await channel.send(self.battle.levelup_message())
                                await self.battle.bot_mes.add_reaction('🇻')
                                await self.battle.bot_mes.add_reaction('🇩')
                            elif self.battle.Tlevelup and not self.battle.Tlevelup_message:
                                await channel.send(self.battle.levelup(emoji))
                            else:
                                self.battle.Tlevelup = False

                        if not self.battle.Tlevelup:
                            self.battle.reset()
                            self.battle.bot_mes = await channel.send(self.battle.attack(emoji))
                            for e in self.battle.to_add():
                                await self.battle.bot_mes.add_reaction(e)

        @self.event
        async def on_voice_state_update(member, before, after):
            self.logger.log_voice(member, before, after)
            channel = after.channel
            if channel is None:
                return
            channel_num = len(channel.members)
            cotoco = member
            channel_with_members, _ = get_people(channel.guild, debug=False)
            people_num = len(channel_with_members.members)
            if cotoco.id == 296428510145282048 and channel != channel_with_members and people_num > 1 and channel_num == 1:  # never leave Cotoco in a voice server alone
                if channel.id != 338442685423550475:
                    print(f'moving cotoco to {channel_with_members}')
                    await cotoco.move_to(channel_with_members)
                    await bot.get_channel(338441688840142850).send('cotoco cara, vai se socializar')

            if channel == channel_with_members and member.id != self.slave_id and before.channel != after.channel and member.guild.id == 338441688840142850:  # greetings
                if member.id in self.channel_banned:  # kicks channel-banned people
                    await member.move_to(None)
                else:

                    def excluir():
                        os.remove("output.mp3")

                    voice = get(bot.voice_clients, guild=member.guild)
                    try:  # tries to join the same voice channel as the user
                        if voice and voice.is_connected():
                            await voice.move_to(channel)
                        else:
                            await channel.connect()
                    except:
                        pass
                    voice = get(bot.voice_clients, guild=member.guild)

                    if random.randint(1, 150) == 1:  # small chance of kicking the user (joke)
                        if not voice.is_playing():
                            output = gtts.gTTS(text=f'Você não, ninguém gosta de você babaca', lang='pt', slow=False)
                            output.save("output.mp3")

                            voice.play(discord.FFmpegPCMAudio("output.mp3"), after=lambda e: excluir())
                            voice.source = discord.PCMVolumeTransformer(voice.source)
                            voice.source.volume = self.volume * 5
                            await asyncio.sleep(4.5)
                            await member.move_to(None)
                    else:
                        if member.id == self.master_id:  # i have the power
                            name = 'dono'
                        else:
                            name = member.name.lower()

                        if not voice.is_playing():  # custom greetings
                            # if name == 'adonay':
                            #     voice.play(discord.FFmpegPCMAudio(f'{self.path}/misc/adonay-alternative-name.mp3'))
                            #     voice.source = discord.PCMVolumeTransformer(voice.source)
                            #     voice.source.volume = self.volume * 5
                            # else:
                            if name == 'yuurikyo':
                                voice.play(discord.FFmpegPCMAudio(f'{self.path}/soundboard/hi-honey.mp3'))
                                voice.source = discord.PCMVolumeTransformer(voice.source)
                                voice.source.volume = self.volume * 0.8
                            elif name == 'cafu_cotoco':
                                voice.play(discord.FFmpegPCMAudio(f'{self.path}/misc/cotoco-alternative-name.mp3'))
                                voice.source = discord.PCMVolumeTransformer(voice.source)
                                voice.source.volume = self.volume * 5
                            else:
                                output = gtts.gTTS(text=f'oi {name}', lang='pt')
                                output.save("output.mp3")

                                voice.play(discord.FFmpegPCMAudio("output.mp3"), after=lambda e: excluir())
                                voice.source = discord.PCMVolumeTransformer(voice.source)
                                voice.source.volume = self.volume * 5

        @self.event
        async def on_member_join(member):  # greeting new users in the guild (only one guild)
            self.joining_member = member.id
            if member.guild.id == 338441688840142850:
                await member.edit(nick=f'PATO_{member.name}')

                await self.get_channel(482949972141277194).send(
                    f'A Mamãe falou quack quack e o(a) {member.nick} chegou!! Bem vindo(a)!')
                self.joining_member = None

        @self.event
        async def on_member_update(before, after):  # monitors everyone's name (only one guild)
            if after.guild.id == 338441688840142850:
                if after.nick is not None:
                    if 'PATO_' not in after.nick:
                        print(f'{after.nick} from {after.guild} tried to remove PATO_ from nick')
                        print('nick')
                        await after.edit(nick=f'PATO_{after.nick}')
                        await bot.get_channel(338441688840142850).send(f'{after.name} Tentou tirar o PATO do nome')
                else:
                    if self.joining_member != after.id:
                        print(f'{after.name} from {after.guild} tried to remove PATO_ from nick')
                        print('name')
                        await after.edit(nick=f'PATO_{after.name}')
                        await bot.get_channel(338441688840142850).send(f'{after.name} Tentou tirar o PATO do nome')

        @self.command(pass_context=True)
        async def teste(ctx):
            try:
                for guild in self.music_message:
                    msgid = int(self.music_message[guild])
                    msg = await ctx.fetch_message(msgid)
                    await msg.add_reaction('⏯')
                    await msg.add_reaction('⏹')
                    await msg.add_reaction('⏭')
            except:
                pass

        @self.command(pass_context=True)
        async def set_music(ctx):
            await ctx.message.delete()

            with shelve.open(f'{self.path}/database/music/music') as music:
                guild_id = str(ctx.guild.id)
                if guild_id in music and music[guild_id] == ctx.channel.id:
                    await ctx.send("esse canal ja ta setado")
                elif guild_id in music:
                    music[guild_id] = ctx.channel.id
                else:
                    music[guild_id] = ctx.channel.id
                    self.music = dict(music)

                with shelve.open(f'{self.path}/database/music/music_message') as music_message:
                    embed = self.music_embed_idle()

                    message = await bot.get_channel(int(music[guild_id])).send(embed=embed)
                    await message.add_reaction('⏯')
                    await message.add_reaction('⏹')
                    await message.add_reaction('⏭')

                    self.music_message[guild_id] = message.id
                    music_message[guild_id] = message.id

        @self.command(pass_context=True)
        async def remove_music(ctx):
            await ctx.message.delete()

            with shelve.open(f'{self.path}/database/music/music') as music:
                guild_id = str(ctx.guild.id)
                if guild_id in music and music[guild_id] == ctx.channel.id:
                    del music[guild_id]
                    await ctx.send('canal removido')
                elif guild_id in music and music[guild_id] != ctx.channel.id:
                    await ctx.send('nao eh este canal q ta setado')
                elif guild_id not in music:
                    await ctx.send('nenhum canal deste servidor lindo esta setado')
                self.music = dict(music)

                with shelve.open(f'{self.path}/database/music/music_message') as music_message:
                    message = await ctx.fetch_message(int(music_message[guild_id]))
                    await message.delete()
                    del self.music_message[guild_id]
                    del music_message[guild_id]

        @self.command(pass_context=True)
        async def play(ctx):  # play youtube music
            url = content(ctx)

            try:
                try:
                    await ctx.delete()
                except:
                    await ctx.message.delete()
            except:
                pass

            if 'http' in url:
                async def queue(replay=False):
                    if replay:
                        del self.queue[guild_id][0]

                    if len(self.queue[guild_id]) == 0:
                        embed = self.music_embed_idle()

                        msg_id = int(self.music_message[str(ctx.guild.id)])
                        msg = await ctx.channel.fetch_message(msg_id)
                        await msg.edit(embed=embed)
                    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 4294',
                                      'options': '-vn'}
                    with youtube_dl.YoutubeDL({'format': 'bestaudio'}) as ydl:
                        try:
                            info = ydl.extract_info(self.queue[guild_id][0][0], download=False)
                        except:
                            pass
                        URL = info['formats'][0]['url']

                    embed = await self.music_embed_update(info, guild_id)

                    msg_id = int(self.music_message[str(ctx.guild.id)])
                    try:
                        msg = await ctx.channel.fetch_message(msg_id)
                        await msg.edit(embed=embed)
                    except:
                        for i in ctx.guild.text_channels:
                            try:
                                msg = await i.fetch_message(msg_id)
                                await msg.edit(embed=embed)
                            except:
                                pass

                    voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS),
                               after=lambda e: asyncio.run_coroutine_threadsafe(queue(True), bot.loop))
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = self.volume

                guild_id = ctx.guild.id
                if guild_id not in self.queue:
                    self.queue[guild_id] = []

                voice = get(bot.voice_clients, guild=ctx.guild)
                try:  # tries to join the same voice channel as the user
                    await join(ctx)
                except:
                    pass
                voice = get(bot.voice_clients, guild=ctx.guild)

                if 'list=' in url:
                    with youtube_dl.YoutubeDL({'format': 'bestaudio'}) as ydl:
                        vids = ydl.extract_info(url, download=False)

                        for i, info in enumerate(vids['entries']):
                            self.queue[guild_id].append((vids["entries"][i]["webpage_url"],
                                                         vids["entries"][i]["title"]))
                else:
                    with youtube_dl.YoutubeDL({'format': 'bestaudio'}) as ydl:
                        try:
                            info = ydl.extract_info(url, download=False)
                        except:
                            pass
                        self.queue[guild_id].append((url, info['title']))

                if voice.is_playing():
                    with youtube_dl.YoutubeDL({'format': 'bestaudio'}) as ydl:
                        try:
                            info = ydl.extract_info(self.queue[guild_id][0][0], download=False)
                        except:
                            pass
                    embed = await self.music_embed_update(info, guild_id)

                    msg_id = int(self.music_message[str(ctx.guild.id)])
                    msg = await ctx.channel.fetch_message(msg_id)
                    await msg.edit(embed=embed)
                else:
                    await queue()
            elif ctx.guild.id not in self.searching or not self.searching[ctx.guild.id]:
                msg = ''
                results = YoutubeSearch(url, max_results=10).to_json()
                data = json.loads(results)
                self.vids.append(ctx)
                for idx, info in enumerate(data['videos']):
                    self.vids.append((info['title'], 'https://www.youtube.com/watch?v=' + info['id']))
                    msg += f'{idx + 1} : {info["title"]} \n'
                self.searching[ctx.guild.id] = True

                embed = discord.Embed(title=f'Pick one:', description=f'{msg}\nSend 0 to cancel',
                                      color=discord.Color.red())
                msg2 = await ctx.channel.send(embed=embed)
                self.vids[0] = (self.vids[0], msg2)

        @self.command(pass_context=True)
        async def live(ctx):
            url = content(ctx)

            try:
                await join(ctx)
            except:
                pass
            voice = get(bot.voice_clients, guild=ctx.guild)

            player = await YTDLSource.from_url(url, loop=self.loop,
                                               stream=True)
            if not voice.is_playing():
                try:
                    voice.play(player, after=lambda e: print(f'error: {e}'))
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = self.volume * 5
                except:
                    pass

        @self.command(pass_context=True)
        async def stop(ctx, guild=None):
            if guild is None:
                guild = ctx.guild

            voice = get(bot.voice_clients, guild=guild)
            if voice is not None:
                voice.stop()
                self.queue[guild.id].clear()

        @self.command(pass_context=True)
        async def skip(ctx, guild=None):
            if guild is None:
                guild = ctx.guild

            voice = get(bot.voice_clients, guild=guild)

            if voice and voice.is_playing():
                voice.stop()
                print("music skiped")
            else:
                print("no music playing failed to skip")

        @self.command(pass_context=True)
        async def pause(ctx, guild=None):
            if guild is None:
                guild = ctx.guild

            voice = get(bot.voice_clients, guild=guild)

            if voice and voice.is_playing():
                print("music paused")
                voice.pause()
            else:
                print("music not playing, failed to pause")

        @self.command(pass_context=True)
        async def resume(ctx, guild=None):
            if guild is None:
                guild = ctx.guild
            voice = get(bot.voice_clients, guild=guild)

            if voice and voice.is_paused():
                print("resuming")
                voice.resume()
            else:
                print("musica n ta pausada")

        @self.command(pass_context=True)
        async def join(ctx, channel=None):
            if channel:
                guild = channel.guild
            else:
                channel = ctx.message.author.voice.channel
                guild = ctx.guild
            voice = get(bot.voice_clients, guild=guild)
            if voice and voice.is_connected():
                await voice.move_to(channel)
            else:
                await channel.connect()

        @self.command(pass_context=True)
        async def leave(ctx):
            voice = get(bot.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected():
                await voice.disconnect()

        @self.command(pass_context=True)
        async def sb(ctx, file: str, numero=1):  # sound board
            try:
                await join(ctx)
            except Exception:
                pass

            if os.path.isfile(f'{self.path}/soundboard/{file}.mp3'):
                if numero < 10:
                    def repetir(vezes):
                        if vezes > 0:
                            vezes -= 1
                            print(file)
                            voice.play(discord.FFmpegPCMAudio(f'{self.path}/soundboard/{file}.mp3'),
                                       after=lambda e: repetir(vezes))
                            voice.source = discord.PCMVolumeTransformer(voice.source)
                            voice.source.volume = self.volume

                    voice = get(bot.voice_clients, guild=ctx.guild)
                    repetir(numero)
                else:
                    await ctx.send("pf poupe meus ouvidos e dx o numero abaixo de 10")
            else:
                await ctx.send(
                    f"use o comando //sbfiles para ver os sons disponiveis, se quiser q eu adicione {file} fale com "
                    f"o meu mestre")

        @self.command(pass_context=True)
        async def sbfiles(ctx):  # sound board files
            embed = discord.Embed(color=discord.Color.gold())
            embed.set_author(name='Soundboard')
            files = ""
            for file in os.listdir(f'{self.path}/soundboard'):
                files += file.replace(".mp3", "") + "\n"
            embed.add_field(name='sons:', value=files, inline=False)
            await ctx.send(embed=embed)

        @self.command(pass_context=True)
        async def sbmy(ctx, recom: str = None):  # user saved sound board
            sb = shelve.open(f'{self.path}/database/sb/sb')
            if recom:
                key = recom
            else:
                key = str(ctx.author.id)
            saved = sb[key]
            saved = sorted(saved)
            embed = discord.Embed(color=discord.Color.gold())
            embed.set_author(name=f"{ctx.author.nick}'s Soundboard")
            files = ""
            for file in saved:
                files += file + "\n"
            embed.add_field(name='sons:', value=files, inline=False)
            await ctx.send(embed=embed)
            sb.close()

        @self.command(pass_context=True)
        async def sbsave(ctx, file: str):  # saves sound to user sound board
            if os.path.isfile(f'{self.path}/soundboard/{file}.mp3'):
                sb = shelve.open(f'{self.path}/database/sb/sb')
                key = str(ctx.author.id)
                if key in sb.keys():
                    sb_temp = sb[key]
                    sb_temp.append(file)
                else:
                    sb_temp = [file]
                sb[key] = sb_temp
                sb.close()
            else:
                await ctx.send(
                    f"use o comando //sbfiles para ver os sons disponiveis, se quiser q eu adicione {file} fale com "
                    f"o meu mestre")

        @self.command(pass_context=True)
        async def sbremove(ctx, file: str):
            sb = shelve.open(f'{self.path}/database/sb/sb')
            key = str(ctx.author.id)
            if key in sb.keys():
                temp = sb[key]
                if file in temp:
                    temp.remove(file)
                    sb[key] = temp
                else:
                    await ctx.send(f'vc n tem {file} adicionado')
            else:
                await ctx.send('vc nem tem nada salvo bbk')

        @self.command(pass_context=True)
        async def sbrecommended(ctx):
            recommended = str(self.master_id)
            await sbmy(ctx, recommended)

        @self.command(pass_context=True)
        async def entrar(ctx):
            canal = content(ctx)
            found = False
            for channel in ctx.guild.voice_channels:
                if channel.name.lower() == canal.lower():
                    found = True
                    voice = get(bot.voice_clients, guild=ctx.guild)
                    if voice and voice.is_connected():
                        await voice.move_to(channel)
                    else:
                        await channel.connect()
            if not found:
                await ctx.send(f"nao achei o canal ({canal})")

        @self.command(pass_context=True)
        async def set_anime(ctx):
            animes = shelve.open(f'{self.path}/database/animes/animes_guild')
            anime_keys = list(animes.keys())
            guild_id = str(ctx.guild.id)
            if guild_id in anime_keys and animes[guild_id] == ctx.channel.id:
                await ctx.send("esse canal ja ta setado")
            elif guild_id in anime_keys:
                await ctx.send(f'mudando do canal "{bot.get_channel(animes[guild_id])}" para esse')
                animes[guild_id] = ctx.channel.id
            else:
                await ctx.send("canal setado")
                animes[guild_id] = ctx.channel.id
            animes.close()

        @self.command(pass_context=True)
        async def unset_anime(ctx):
            animes = shelve.open(f'{self.path}/database/animes/animes_guild')
            anime_keys = list(animes.keys())
            guild_id = str(ctx.guild.id)
            if guild_id in anime_keys and animes[guild_id] == ctx.channel.id:
                await ctx.send("Removendo este canal da lista")
                del animes[guild_id]
            elif guild_id in anime_keys:
                await ctx.send(f"Este nao eh o canal setado, eh o '{bot.get_channel(animes[guild_id])}'")
            else:
                await ctx.send("Este server nao tem nenhum canal setado, //set_anime para setar um canal")
            animes.close()

        @self.command(pass_context=True)
        async def my_anime(ctx):
            animes = shelve.open(f'{self.path}/database/animes/animes_list')
            user_id = str(ctx.message.author.id)
            if user_id not in list(animes.keys()):
                await ctx.send('vc n tem uma lista de animes, adicione um para criar uma')
            else:
                send = ''
                for anime in animes[user_id]:
                    send += f'{anime}\n'
                send = '\n'.join(sorted(send.split('\n')))
                await ctx.send(f'Sua lista de animes:{send}')
            animes.close()

        @self.command(pass_context=True)
        async def add_anime(ctx):
            animes = shelve.open(f'{self.path}/database/animes/animes_list')
            user_id = str(ctx.message.author.id)
            anime_name = content(ctx)
            if user_id in list(animes.keys()):
                anime_list = animes[user_id]
                anime_list.append(anime_name)
                animes[user_id] = anime_list
            else:
                animes[user_id] = [anime_name]
            animes.close()
            await my_anime(ctx)

        @self.command(pass_context=True)
        async def remove_anime(ctx):
            animes = shelve.open(f'{self.path}/database/animes/animes_list')
            user_id = str(ctx.message.author.id)
            anime_name = content(ctx)
            if user_id in list(animes.keys()):
                anime_list = animes[user_id]
                anime_list.remove(anime_name)
                animes[user_id] = anime_list

                if len(animes[user_id]) == 0:
                    del animes[user_id]
                await my_anime(ctx)
            else:
                await ctx.send('vc n tem nem lista, vai tira oq dela??')

            animes_tracking = shelve.open(f'{self.path}/database/animes/animes_track')
            animes_check = []
            for key in list(animes.keys()):
                for anime_in_list in animes[key]:
                    if anime_in_list not in animes_check and list_similar(anime_in_list, animes_check) < 0.6:
                        animes_check.append(anime_in_list.lower())
            if list_similar(anime_name, animes_check) < 0.6:
                if anime_name.lower() in list(animes_tracking.keys()):
                    del animes_tracking[anime_name.lower()]

            animes.close()

        @self.command(pass_context=True)
        async def clear_anime(ctx):
            animes = shelve.open(f'{self.path}/database/animes/animes_list')
            user_id = str(ctx.message.author.id)
            if user_id in list(animes.keys()):
                del animes[user_id]
                await ctx.send('lista limpada')
            else:
                await ctx.send('vc n tem nem lista, vai limpar oq dela??')

            if len(list(animes.keys())) == 0:
                to_clear = shelve.open(f'{self.path}/database/animes/animes_track')
                to_clear.clear()

            animes.close()

        @self.command(pass_context=True)
        async def hiragana(ctx):
            self.hiragana = True
            self.jap = japanese(ctx.message.channel.id)

        @self.command(pass_context=True)
        async def katakana(ctx):
            self.katakana = True
            self.jap = japanese(ctx.message.channel.id)

        @self.command(pass_context=True)
        async def spasm(ctx, times=1):
            channel = ctx.message.author.voice.channel

            try:
                voice = get(bot.voice_clients, guild=ctx.guild)
                if voice.is_connected():
                    await voice.disconnect()
            except Exception:
                pass

            for i in range(times):
                try:
                    voice = await channel.connect()
                except Exception:
                    voice = None
                    print("alguma coisa deu merda ao conectar")
                try:
                    await voice.disconnect()
                except Exception:
                    print("alguma coisa deu merda ao desconectar")
                print(f"torturado {i} vezes")

        @self.command(pass_context=True, aliases=['t'])
        async def tts(ctx):
            def excluir():
                os.remove("output.mp3")

            possible_langs = list(gtts.lang.tts_langs().keys())

            contents = content(ctx)
            tld = 'com'
            if contents.startswith('!'):
                lang, frase = contents.replace('!', '').split(' ', 1)
                if '.' in lang:
                    tld = lang.split('.', 1)[1]
                    lang = lang.split('.')[0]
            else:
                lang = 'pt'
                frase = contents

            if lang not in possible_langs:
                await ctx.send("nao conheco essa lingua")

            voice = get(bot.voice_clients, guild=ctx.guild)
            try:
                if voice is None:
                    await join(ctx)
            except:
                pass
            voice = get(bot.voice_clients, guild=ctx.guild)

            if frase == "":
                await ctx.send(f"Erro, exemplo deste comando: {self.P}t teste")

            if not voice.is_playing():
                output = gtts.gTTS(text=frase, lang=lang, tld=tld, slow=False)
                output.save("output.mp3")

                voice.play(discord.FFmpegPCMAudio("output.mp3"), after=lambda e: excluir())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = self.volume * 5
            else:
                await ctx.send("to tocando perae")

        @self.command(pass_context=True)
        async def Aa(ctx):
            frase = content(ctx)

            if frase == "":
                await ctx.send(f"Erro, exemplo deste comando: {self.P}Aa teste")
            else:
                await ctx.send(foo(frase))

        @self.command(pass_context=True)
        async def morse(ctx):
            frase = content(ctx)

            if frase == "":
                await ctx.send(f"Erro, exemplo deste comando: {self.P}morse teste")
            else:
                message = content(ctx).upper()
                carry = 0
                for i in message:
                    if i in self.MORSE_CODE_DICT:
                        carry = 1
                    else:
                        carry = 0

                if carry == 1:
                    await ctx.send(encrypt(message.upper()))
                else:
                    await ctx.send(decrypt(message).lower())

        @self.command(pass_context=True)
        async def say(ctx):
            frase = content(ctx)

            if frase == '':
                await ctx.send(f'Erro, exemplo deste comando: {self.P}say teste')
            else:
                await ctx.message.delete()
                await ctx.send(frase)

        @self.command(pass_context=True)
        async def time(ctx):
            nomes = content(ctx).split(' ')
            nomes_random = random.sample(nomes, len(nomes))
            time1 = nomes_random[:len(nomes_random) // 2]
            time2 = nomes_random[len(nomes_random) // 2:]
            await ctx.send(' - '.join(time1) + "\n" + ' - '.join(time2))

        @self.command(pass_context=True)
        async def joguinho(ctx):
            player = rpg.Mage(ctx)
            enemy = rpg.Zombie()
            message = await ctx.send(f'{enemy.name} = {enemy.life:.2f} (-0)\nVoce = {player.life:.2f} (-0)')
            await message.add_reaction("🇶")
            await message.add_reaction("🇼")
            self.battle = rpg.Battle(player)
            self.battle.set(enemy, message)
            self.rpg = True

        @self.command(pass_context=True)
        async def helpjogo(ctx):
            await ctx.send(f"Digite {self.P}joguinho para comecar um novo jogo\n"
                           "Voce comeca com 2 habilidades\n"
                           "Q = lanca uma bola de fogo que causa dano no inimigo\n"
                           "W = usa a magia instantanea heal, ela cura 40% da vida base\n"
                           "Apos matar o inimigo, voce tera chance de dropar ou uma espada ou uma armadura\n"
                           "Voce Podera trocar seu equipamento atual pelo loot se desejar\n"
                           "Apos acumular 10 de XP voce subira de nivel, podendo escolher aumentar "
                           "a vida base ou o dano base\n"
                           "Voce podera desbloquear novas habilidades conforme joga\n"
                           "E = da 80% do dano base porem coloca fogo no inimigo, dando 20% do dano base pelos "
                           "proximos 4 rounds\n"
                           "R = triplica o efeito da proxima habilidade, porem possui o cooldown de 6 rounds")

        @self.command(pass_context=True)
        async def leaderboard(ctx):
            embed = discord.Embed(color=discord.Color.gold())
            embed.set_author(name='Leaderboard')
            embed.add_field(name='FlipDolan',
                            value='o com menos vida, chegou no lvl 650, seu maior dano foi de 133070.26, '
                                  'vida base de 3212hp e dano base de 1002', inline=False)
            await ctx.send(embed=embed)

        @self.command(pass_context=True)
        async def joguinho2(ctx, user: discord.Member):
            self.tic = TicTacToe(ctx.message.author, user)
            self.tic.player1 = not self.tic.player1
            temp_message = f'Vez do {self.tic.get_playing_name()}\n'
            temp_message += self.tic.draw(emojy=True)
            message = await ctx.send(temp_message)
            self.tic.set_message(message)
            self.tic_tac_toe = True

        @self.command(pass_context=True)
        async def r(ctx):
            roll = content(ctx).lower()
            nums = roll.split('d')
            dados = int(nums[0])
            if '+' in nums[1]:
                lados, offset = nums[1].split('+')
            else:
                lados = int(nums[1])
                offset = 0

            frase = ''
            resultado = 0
            for _ in range(dados):
                no_bug = random.randint(1, int(lados))
                frase += str(no_bug) + " + "
                resultado += no_bug
            frase = ''.join(frase.rsplit(" + ", 1))

            if offset != 0:
                str_offset = f'+ {offset} '
                resultado += int(offset)
            else:
                str_offset = ''

            if " " in frase or str_offset != "":
                await ctx.send(f"Os dados rolaram {frase} {str_offset}= {resultado}")
            else:
                await ctx.send(f"O dado rolou {frase} {str_offset}")

        @self.command(pass_context=True)
        async def fight(ctx):
            if not self.fight:
                self.fight = True
                monsters = content(ctx)
                monsters = monsters.split(' ')
                for monster in monsters:
                    self.fight_dict[monster] = random.randint(1, 100)
            else:
                self.fight = False
                fight_list = sorted(self.fight_dict.items(), key=itemgetter(1), reverse=True)
                to_send = ''
                for person, roll in fight_list:
                    to_send += f'{person}: {roll}\n'
                await ctx.send(to_send)
                self.fight_dict = {}

        @self.command(pass_context=True)
        async def herele(ctx):
            pfp = bot.get_user(248791652343349249).avatar_url
            await ctx.send("herele")
            await ctx.send(pfp)

        @self.command(pass_context=True)
        async def yuurikyo(ctx):
            pfp = bot.get_user(335931758270873602).avatar_url
            await ctx.send("yuri")
            await ctx.send(pfp)

        @self.command(pass_context=True)
        async def flip(ctx):
            pfp = bot.get_user(277996848587997184).avatar_url
            await ctx.send("Flip Mestre dos mangos supremo senhor do universo")
            await ctx.send(pfp)

        @self.command(pass_context=True)
        async def casar(ctx, user: discord.Member):
            casados = shelve.open(f'{self.path}/database/casados/casados')
            key_list = list(casados.keys())
            if ctx.author.name in key_list and user.name in key_list:  # burrice
                await ctx.send("krl tu eh burro, vcs ja tao casados mongo")
            else:
                if ctx.author.name in key_list:  # traindo
                    autor = ctx.author.name
                    await ctx.send(
                        f"ooooopa {autor}, acho q tua amada {casados[autor]} nao vai gosta nem um pouco disso")
                elif user.name in key_list:  # tentando chifrar
                    await ctx.send(f"hehehe ta tentando chifrar o {casados[user.name]}? eles ja tao casados meu filho")
                else:  # wholesome
                    embed = discord.Embed(color=discord.Color.dark_red())
                    embed.add_field(name=user.name, value=f'foi pedido em casamento por: {ctx.author.name}')
                    embed.set_image(url=user.avatar_url)

                    msg = await ctx.send(embed=embed)
                    await msg.add_reaction('💘')
                    await msg.add_reaction('💔')
                    self.casando = True
                    self.casando_p = ctx.author
                    self.casando_u = user

        @self.command(pass_context=True)
        async def pp(ctx, user: discord.Member):
            await ctx.message.delete()
            pfp = user.avatar_url
            await ctx.send(f"foto de perfil do usuario: {user.name}")
            await ctx.send(pfp)

        @self.command(pass_context=True)
        async def ban(ctx, user: discord.Member):
            await ctx.message.delete()
            ide = user.id
            if user.id == self.master_id:
                await ctx.send("Quem ousa remover os poderes do incrivel fosguesterolerolero???? Va para a jaula agora")
                await jaula(ctx, ctx.message.author)
            elif ide not in self.banned:
                self.banned.append(ide)
                print(f"{user.name} banned")
                await ctx.send(f"{user.name} foi banido, fica quieto agr")
            else:
                await ctx.send("ele ja ta banido poha")

        @self.command(pass_context=True)
        async def unban(ctx, user: discord.Member):
            await ctx.message.delete()
            ide = user.id
            if ide in self.banned:
                self.banned.remove(ide)
                print(f"{user.name} unbanned")
                await ctx.send(f"{user.name} foi desbanido, eu n aconselho mas fzr oq")
            else:
                await ctx.send("ele ja ta desbanido")

        @self.command(pass_context=True)
        async def ban_list(ctx):
            aaa = ""
            for person in self.banned:
                aaa += bot.get_user(person).name + "\n"
            await ctx.send(aaa)

        @self.command(pass_context=True)
        async def channel_ban(ctx, user: discord.Member):
            await ctx.message.delete()
            ide = user.id
            if user.id == self.master_id:
                await ctx.send("Quem ousa remover os poderes do incrivel fosguesterolerolero???? Va para a jaula agora")
                await jaula(ctx, ctx.message.author)
            elif ide not in self.banned:
                self.channel_banned.append(ide)
                print(f"{user.name} banned")
                await ctx.send(f"{user.name} foi banido, fica quieto agr")
            else:
                await ctx.send("ele ja ta banido poha")

        @self.command(pass_context=True)
        async def channel_unban(ctx, user: discord.Member):
            await ctx.message.delete()
            ide = user.id
            if ide in self.channel_banned:
                self.channel_banned.remove(ide)
                print(f"{user.name} unbanned")
                await ctx.send(f"{user.name} foi desbanido, eu n aconselho mas fzr oq")
            else:
                await ctx.send("ele ja ta desbanido")

        @self.command(pass_context=True)
        async def channel_ban_list(ctx):
            aaa = ''
            for person in self.channel_banned:
                aaa += bot.get_user(person).name + '\n'
            await ctx.send(aaa)

        @self.command(pass_context=True)
        async def mute(ctx, user: discord.Member):
            await ctx.message.delete()
            await user.edit(mute=True)
            await user.edit()

        @self.command(pass_context=True)
        async def unmute(ctx, user: discord.Member):
            await ctx.message.delete()
            await user.edit(mute=False, deafen=False)

        @self.command(pass_context=True)
        async def jaula(ctx, user: discord.Member):
            print(f"{ctx.message.author.name} usou o comando jaula no {user}")
            await ctx.message.delete()
            guild = ctx.guild
            channel = None

            for channels in guild.voice_channels:
                if 'jaula' in channels.name.lower():
                    channel = channels

            if channel is None:
                await ctx.send("esse servidor n tem jaula")
                return

            voice = get(bot.voice_clients, guild=guild)

            if user.id == self.master_id:
                user = ctx.message.author
                await ctx.send("VOCE NAO PODE ENJAULAR O ENJAULADOR")

            await user.move_to(channel)
            if voice and voice.is_connected():
                await voice.disconnect()
            voice = await channel.connect()

            while True:
                if len(channel.members) < 2:
                    return
                try:
                    voice = await channel.connect()
                    print("entrei na jaula")
                except:
                    print("alguma coisa deu merda ao conectar")
                try:
                    await voice.disconnect()
                    print("sai da jaula")
                except:
                    print("alguma coisa deu merda ao desconectar")

        @self.command(pass_context=True)
        async def limar(ctx, user: discord.Member, num: int = None):
            if num:
                pass
            msg = await ctx.send('a limar')
            for _ in range(2):
                for _ in range(3):
                    await asyncio.sleep(2)
                    await msg.edit(content=f'{msg.content}.')
                await msg.edit(content=f'{msg.content[0:7]}')
            await ctx.send(f'{user.nick} foi limado, agradeco a atencao')

        @self.command(pass_context=True)
        async def limpar(ctx, user: discord.Member, num: int):
            await ctx.message.delete()
            history = await ctx.channel.history(limit=num).flatten()
            for menssage in history:
                if menssage.author == user:
                    await menssage.delete()
                    print(f'Excluindo: "{menssage.content}" por {menssage.author.name}')
            print("terminou de limpar")

        @self.command(pass_context=True)
        async def i2a(ctx):
            img = content(ctx)
            if img == '':
                img = ctx.message.attachments[0].url
            if type(img) == str:
                pic = requests.get(img)
                if pic.ok:
                    img = cv2.imdecode(np.frombuffer(pic.content, np.uint8), -1)

            text = img2ascii(img).split('\n')
            for x in range(5):
                a = ''
                for y in range(10):
                    a += text[x * 10 + y] + '\n'
                await ctx.send(a)
            await ctx.send('---done---')

        @self.command(pass_context=True)
        async def create_account(ctx):
            money = shelve.open(f'{self.path}/database/money/money')
            owner = str(ctx.message.author.id)
            if owner in list(money.keys()):
                await ctx.send("voce ja possui uma conta seu bobo")
            else:
                money[owner] = 0
                await ctx.send("conta criada, atualmente voce possui 0 dinheiros")
            money.close()

        @self.command(pass_context=True)
        async def wallet(ctx):
            money = shelve.open(f'{self.path}/database/money/money')
            owner = str(ctx.message.author.id)
            if owner in list(money.keys()):
                await ctx.send(f"atualmente voce possui {money[owner]} dinheiros")
            else:
                await ctx.send("por favor crie uma conta usando o //create_account")
            money.close()

        @self.command(pass_context=True)
        async def add(ctx, quantity: float):
            money = shelve.open(f'{self.path}/database/money/money')
            owner = str(ctx.message.author.id)
            quantity = round(quantity, 2)
            if owner in list(money.keys()):
                print(round(money[owner] + quantity, 2))
                money[owner] = round(money[owner] + quantity, 2)
                await ctx.send(f"+{quantity} dinheiros adicionados, atualmente voce possui {money[owner]} dinheiros")
            else:
                await ctx.send("por favor crie uma conta usando o //create_account")
            money.close()

        @self.command(pass_context=True)
        async def reset(ctx):
            money = shelve.open(f'{self.path}/database/money/money')
            owner = str(ctx.message.author.id)
            if owner in list(money.keys()):
                money[owner] = 0
                await ctx.send(f"conta resetada, atualmente voce possui {money[owner]} dinheiros")
            else:
                await ctx.send("por favor crie uma conta usando o //create_account")
            money.close()

        @self.command(pass_context=True)
        async def reset_user(ctx, user: discord.Member):
            if ctx.message.author.id == self.master_id:
                money = shelve.open(f'{self.path}/database/money/money')
                owner = str(user.id)
                if owner in list(money.keys()):
                    money[owner] = 0
                    await ctx.send(f"conta resetada, atualmente {user.name} possui {money[owner]} dinheiros")
                else:
                    await ctx.send("por favor crie uma conta usando o //create_account")
                money.close()
            else:
                await jaula(ctx, ctx.message.author)

        @self.command(pass_context=True)
        async def set_discount(ctx):
            storage = shelve.open(f'{self.path}/database/storage/storage')
            if ctx.guild.name in storage and bot.get_channel(storage[ctx.guild.name]) == ctx.channel:
                await ctx.send("esse canal ja ta setado")
            elif ctx.guild.name in storage:
                await ctx.send(f'mudando do canal "{bot.get_channel(storage[ctx.guild.name])}" para esse')
                storage[ctx.guild.name] = ctx.channel.id
            else:
                await ctx.send("canal setado")
                storage[ctx.guild.name] = ctx.channel.id
            storage.close()

        @self.command(pass_context=True)
        async def remove_discount(ctx):
            storage = shelve.open(f'{self.path}/database/storage/storage')
            if ctx.guild.name in storage and bot.get_channel(storage[ctx.guild.name]) == ctx.channel:
                del storage[ctx.guild.name]
                await ctx.send("esse canal foi removido da lista de disconto")
            else:
                await ctx.send("esse canal nao esta setado")
            storage.close()

        @self.command(pass_context=True)
        async def set_crackwatch(ctx):
            crack = shelve.open(f'{self.path}/database/crackwatch/crackwatch')
            guild_id = str(ctx.guild.id)
            if guild_id in crack and crack[guild_id] == ctx.channel.id:
                await ctx.send("esse canal ja ta setado")
            elif guild_id in crack:
                await ctx.send(f'mudando do canal "{bot.get_channel(crack[guild_id])}" para esse')
                crack[guild_id] = ctx.channel.id
            else:
                await ctx.send("canal setado")
                crack[guild_id] = ctx.channel.id
            crack.close()

        @self.command(pass_context=True)
        async def remove_crackwatch(ctx):
            crack = shelve.open(f'{self.path}/database/crackwatch/crackwatch')
            crack_keys = list(crack.keys())
            guild_id = str(ctx.guild.id)
            if guild_id in crack_keys and crack[guild_id] == ctx.channel.id:
                await ctx.send("Removendo este canal da lista")
                del crack[guild_id]
            elif guild_id in crack_keys:
                await ctx.send(f"Este nao eh o canal setado, eh o '{bot.get_channel(crack[guild_id])}'")
            else:
                await ctx.send("Este server nao tem nenhum canal setado, //set_anime para setar um canal")
            crack.close()

        @self.command(pass_context=True)
        async def ran_sub(ctx):
            subreddit_name = content(ctx)
            subreddit = await self.reddit.subreddit(subreddit_name)
            try:
                post = await subreddit.random()
                await ctx.send(f'"{post.title}"\n{post.url}')
            except:
                await ctx.send(f"Subreddit {subreddit_name} nao foi encontrado, verifique o nome")

        @self.command(pass_context=True)
        async def set_hino(ctx, horario: str, url: str):
            hinos = shelve.open(f'{self.path}/database/hinos/hinos')
            key = horario.replace(":", "") + str(ctx.message.guild.id)
            if key in list(hinos.keys()):
                await ctx.send(f"removendo o hino do {hinos[key]}")
                os.remove(f"database/hinos/{hinos[key]}")
                del hinos[key]

            results = YoutubeSearch(url.split("&")[0], max_results=1).to_json()
            data = json.loads(results)
            title = data['videos'][0]['title']

            path = os.getcwd() + f"/database/hinos/{title}"
            hinos[key] = title
            os.system(f'youtube-dl -o "{path}.%(ext)s" --extract-audio -x --audio-format mp3 {url}')
            hinos.close()

        @self.command(pass_context=True)
        async def ver_hinos(ctx):
            hinos = shelve.open(f'{self.path}/database/hinos/hinos')
            salvos = ""
            for key in list(hinos.keys()):
                salvos += f"@{key[0:2]}:{key[2:4]} na guild {bot.get_guild(int(key[4:])).name} tocar\n{hinos[key]}\n"
            if salvos != "":
                await ctx.send(salvos)
            else:
                await ctx.send("nao ha nenhum hino babaca")
            hinos.close()

        @self.command(pass_context=True)
        async def apagar_hino(ctx):
            hinos = shelve.open(f'{self.path}/database/hinos/hinos')
            name = content(ctx)
            for key in list(hinos.keys()):
                if hinos[key] == name:
                    try:
                        os.remove(f'{self.path}/database/hinos/{hinos[key]}.mp3')
                        await ctx.send(f"{hinos[key]} apagado")
                        del hinos[key]
                    except:
                        await ctx.send(
                            "algo deu errado e nao foi possivel apagar, pf tente mais tarde, se pa eh pq o hino ta tocando, sla")
            hinos.close()

        @self.command(pass_context=True)
        async def temp(ctx):
            cidade = content(ctx) + " "
            if cidade == "":
                cidade = " sao lourenco"
            cidadee = cidade.replace(" ", "+")
            res = requests.get(f'https://www.google.com/search?q=temperatura{cidadee}', headers=self.headers)
            res.raise_for_status()

            soup = bs4.BeautifulSoup(res.text, "html.parser")
            temperature = soup.find('span', class_="wob_t TVtOme")
            location = soup.find('div', class_="wob_loc mfMhoc")
            try:
                await ctx.send(f"{location.text} : {temperature.text}°C")
            except AttributeError:
                await ctx.send(f"Nao achei a temperatura de{cidade}, ctz q tu tento me trola bbk")

        @self.command(pass_context=True)
        async def clima(ctx):
            cidade = content(ctx)
            if cidade == '':
                cidade = 'Sao Lourenco'
            elif cidade == 'flip':
                cidade = 'porto alegre'
            elif cidade == 'fuguetero':
                cidade = 'santa rita do sapucai'
            elif cidade == 'yuri':
                cidade = 'caraguatatuba'

            weatherDetails = weathercom.getCityWeatherDetails(city=cidade)
            details = json.loads(weatherDetails)

            city = details['city']
            details = details['vt1observation']
            altitude = details['altimeter']
            dewpoint = details['dewPoint']
            feelslike = details['feelsLike']
            humidity = details['humidity']
            obstime = details['observationTime'].split("T")[1].split("-")[0]
            weather = details['phrase']
            precip24Hour = details['precip24Hour']
            snowDepth = details['snowDepth']
            temperature = details['temperature']
            maxtemp = details['temperatureMaxSince7am']
            uvIndex = details['uvIndex']
            visibility = details['visibility']
            windSpeed = details['windSpeed']
            windDir = details['windDirCompass']

            embed = discord.Embed(color=discord.Color.orange())
            embed.set_author(name=city)
            embed.add_field(name='Temperature', value=f'{temperature}°C', inline=True)
            embed.add_field(name='Feels like', value=f'{feelslike}°C', inline=True)
            embed.add_field(name='Max temperature today', value=f'{maxtemp}°C', inline=True)
            embed.add_field(name='Humidity', value=f'{humidity}%', inline=True)
            embed.add_field(name='Weather', value=f'{weather}', inline=True)
            embed.add_field(name='Visibility', value=f'{visibility}km', inline=True)
            embed.add_field(name='Wind speed', value=f'{windSpeed}km/h', inline=True)
            embed.add_field(name='Wind direction', value=f'{windDir}', inline=True)
            embed.add_field(name='Dew point', value=f'{dewpoint}°C', inline=True)
            embed.add_field(name='Observation time', value=f'{obstime}', inline=True)
            embed.add_field(name='Precipitacion on the last 24h', value=f'{precip24Hour}mm', inline=True)
            embed.add_field(name='Snow depth', value=f'{snowDepth}cm', inline=True)
            embed.add_field(name='Uv index', value=f'{uvIndex}', inline=True)
            embed.add_field(name='Altitude', value=f'{altitude}hPa?', inline=True)
            embed.add_field(name='-', value=f'-', inline=True)

            await ctx.send(embed=embed)

        @self.command(pass_context=True)
        async def rank(ctx, mem: discord.Member = None):
            rank = shelve.open(f'{self.path}/database/rank/rank')
            guild = ctx.guild
            print(mem)
            if mem:
                await ctx.message.delete()
                if str(mem.id) in list(rank.keys()):
                    await ctx.send(f'{mem.nick} tem o score de {rank[str(mem.id)]}')
                else:
                    await ctx.send('esse cara eh tao esquecido q n achei ele na lista de ranks')
            else:
                bot_counter = shelve.open(f'{self.path}/database/counter/counter')
                ranks = rank
                ranks[str(self.slave_id)] = bot_counter['good_bot'] - bot_counter['bad_bot']
                for to_test in ranks:
                    member = guild.get_member(int(to_test))
                    if not member:
                        del ranks[to_test]
                    rank = ranks
                sorted_ranks = sorted(ranks.items(), key=itemgetter(1), reverse=True)
                top_five = sorted_ranks[:5]
                worst_five = sorted_ranks[len(sorted_ranks) - 5:]
                top_send = ''
                worst_send = ''
                for rank_id, (name, rank_qnt) in enumerate(top_five):
                    member = guild.get_member(int(name))
                    top_send += f'Rank {rank_id + 1}: {member.nick} with {rank_qnt}\n'
                for rank_id, (name, rank_qnt) in enumerate(worst_five):
                    member = guild.get_member(int(name))
                    worst_send += f'Rank {len(sorted_ranks) - 5 + rank_id + 1}: {member.nick} with {rank_qnt}\n'
                embed = discord.Embed(color=discord.Color.orange())
                embed.set_author(name='Ranks:')
                embed.add_field(name='Top 5:',
                                value=f'{top_send}',
                                inline=False)
                embed.add_field(name='Worst 5:',
                                value=f'{worst_send}',
                                inline=False)
                bot_counter.close()
                await ctx.send(embed=embed)
            rank.close()

        @self.command(pass_context=True)
        async def panela(ctx):
            await ctx.message.delete()
            res = requests.get('https://www.palabrasaleatorias.com/palavras-aleatorias.php', headers=self.headers)
            res.raise_for_status()

            soup = bs4.BeautifulSoup(res.text, "html.parser")
            soup = soup.find('div', style="font-size:3em; color:#6200C5;")
            number = str(random.randint(0, 9)) + str(random.randint(0, 9))
            await ctx.send(f"{soup.text}{number}")

        @self.command(pass_context=True)
        async def todos_panela(ctx):
            if ctx.message.author.id != self.master_id:
                await ctx.send("vc n tem o poder pra fzr isso, membro comum")
                return
            await ctx.message.delete()
            server = ctx.guild
            membros = server.members
            # lista_panela = []
            # await ctx.send("comecando a inventar nomes legais")

            # for _ in membros:
            #     res = requests.get('https://www.palabrasaleatorias.com/palavras-aleatorias.php', headers=self.headers)
            #     res.raise_for_status()
            #
            #     soup = bs4.BeautifulSoup(res.text, "html.parser")
            #     soup = soup.find('div', style="font-size:3em; color:#6200C5;")
            #     number = str(random.randint(0, 9)) + str(random.randint(0, 9))
            #     lista_panela.append(f"{soup.text}{number}")
            # await ctx.send("terminei de inventar nomes legais")

            for membro in membros:
                try:
                    if 'PATO_' not in membro.nick:
                        await membro.edit(nick=f'PATO_{membro.name}')
                        print(membro.nick)
                except:
                    pass

        @self.command(pass_context=True)
        async def kill(ctx):
            print(ctx.message.author.guild_permissions.administrator)
            if ctx.message.author.guild_permissions.administrator:
                await ctx.send("tchaaaaaaaaaaaaaaaaaaaaaaaaaau")
                exit()
            else:
                await ctx.send("Ola membro comum, caso insista no uso deste codigo ira ser banido sem demais avisos")

        @self.command(pass_context=True)
        async def dolar(ctx):
            res = requests.get('https://www.google.com/search?q=dolar', headers=self.headers)
            res.raise_for_status()

            soup = bs4.BeautifulSoup(res.text, "html.parser")
            soup = soup.find('span', class_="DFlfde SwHCTb")
            await ctx.send("R$" + soup.text)

        @self.command(pass_context=True)
        async def euro(ctx):
            res = requests.get('https://www.google.com/search?q=euro', headers=self.headers)
            res.raise_for_status()

            soup = bs4.BeautifulSoup(res.text, "html.parser")
            soup = soup.find('span', class_="DFlfde SwHCTb")
            await ctx.send("R$" + soup.text)

        @self.command(pass_context=True)
        async def russo(ctx):
            res = requests.get('https://www.google.com/search?q=rublo+russo', headers=self.headers)
            res.raise_for_status()

            soup = bs4.BeautifulSoup(res.text, "html.parser")
            soup = soup.find('span', class_="DFlfde SwHCTb")
            await ctx.send("R$" + soup.text)

        @self.command(pass_context=True)
        async def bit(ctx):
            sauce = requests.get("https://www.google.com/search?q=bitcoin", headers=self.headers)
            scr = sauce.content
            soup = bs4.BeautifulSoup(scr, 'lxml')
            bitcoin = soup.find("span", class_="DFlfde SwHCTb")
            await ctx.send(f"R${bitcoin.text}")

        @self.command(pass_context=True)
        async def dodge(ctx):
            sauce = requests.get("https://doge.pt.currencyrate.today/brl", headers=self.headers)
            scr = sauce.content
            soup = bs4.BeautifulSoup(scr, 'lxml')
            dodgel = soup.find_all("span", class_="cc-result", limit=2)
            dodgecoin = dodgel[1].text.replace(" BRL", '')
            await ctx.send(f"R${dodgecoin}")

        @self.command(pass_context=True)
        async def fix_music_messages(ctx):
            for guild in self.music:
                channel = bot.get_channel(self.music[guild])

                # if channel is None:  # deletes unknown channels
                #     del self.music[guild]
                #     del self.music_message[guild]
                #     with shelve.open(f'{self.path}/database/music/music') as music:
                #         music[guild] = self.music
                #
                #     with shelve.open(f'{self.path}/database/music/music_message') as music_message:
                #         music_message[guild] = self.music_message

                mes = await channel.fetch_message(self.music_message[guild])

                reactions = mes.reactions
                if len(reactions) < 3:
                    await mes.clear_reactions()

                    await mes.add_reaction('⏯')
                    await mes.add_reaction('⏹')
                    await mes.add_reaction('⏭')
                else:
                    for reaction in reactions:
                        if reaction.count > 1:
                            async for user in reaction.users():
                                if user.id != self.slave_id:
                                    print(user, reaction)
                                    await mes.remove_reaction(reaction, user)

        @self.command(pass_context=True)
        async def logger_on(ctx):
            if ctx.message.author.id == self.master_id:
                if not self.logger:
                    self.logger = True
                    await ctx.send("logger on")
                else:
                    await ctx.send("logger ja ta on")
            else:
                await ctx.send("sai")

        @self.command(pass_context=True)
        async def logger_off(ctx):
            if ctx.message.author.id == self.master_id:
                if self.logger:
                    self.logger = False
                    await ctx.send("logger off")
                else:
                    await ctx.send("logger ja ta off")
            else:
                await ctx.send("n ha oq vc faça, vc nunca tera privacidade aki")

        @self.command(pass_context=True)
        async def download(ctx):
            await ctx.message.delete()
            if os.path.isdir("D:/Scripts/Python/homework"):
                if ctx.message.author.id == self.master_id:
                    Tchannel = ctx.message.channel
                    history = await Tchannel.history(limit=50).flatten()
                    urls = []
                    slave = bot.get_user(self.slave_id)

                    for message in history:
                        if message.author == slave and message.content == "----------":
                            break
                        elif "http" in message.content:
                            urls.append(message.content)
                        else:
                            try:
                                urls.append(message.attachments[0].url)
                            except:
                                pass

                    if len(urls) > 0:
                        path = f"D:/Scripts/Python/homework/{Tchannel}"
                        pic_num = len(os.listdir(path))
                        x = 0

                        if not os.path.isdir(path):
                            os.mkdir(path)

                        for url in reversed(urls):
                            try:
                                pic = requests.get(url)
                                if pic.ok:
                                    file = open(f"{path}/picture#{x + pic_num}.png", "wb")
                                    file.write(pic.content)
                                    file.close()
                                    x += 1
                            except Exception as e:
                                print(f"Erro ao baixar {url}")
                                print(e)
                            print(url)

                    await ctx.send("----------")
                else:
                    await ctx.send("falei pra n usar")
                    await jaula(ctx, ctx.message.author)
            else:
                m = await ctx.send("Estou no raspberry")
                await asyncio.sleep(2)
                await m.delete()

        @self.command(pass_context=True)
        async def baixar(ctx, url: str):
            if ctx.author.id == self.master_id:
                download_song(url)
            else:
                await ctx.send("NAO")

        @self.command(pass_context=True)
        async def guilds(ctx):
            to_send = ''
            for guild in self.guilds:
                to_send += f'{guild.name} ({guild.id})\n'
            await ctx.send(to_send)

        @self.command(pass_context=True)
        async def voice_channels(ctx):
            guild_name = content(ctx)

            if guild_name == '':
                guild = ctx.guild
            else:
                for g in bot.guilds:
                    if g.name == guild_name:
                        guild = g
                        break
                else:
                    await ctx.send(f'Servidor {guild_name} nao foi encontrado')
                    return

            to_send = ''
            for voice in guild.voice_channels:
                to_send += f'{voice.name} ({voice.id})\n'
            await ctx.send(to_send)

        @self.command(pass_context=True)
        async def text_channels(ctx):
            guild_name = content(ctx)

            if guild_name == '':
                guild = ctx.guild
            else:
                for g in bot.guilds:
                    if g.name == guild_name:
                        guild = g
                        break
                else:
                    await ctx.send(f'Servidor {guild_name} nao foi encontrado')
                    return

            to_send = ''
            for text in guild.text_channels:
                to_send += f'{text.name} ({text.id})\n'
            await ctx.send(to_send)

        @self.command(pass_context=True)
        async def members(ctx):
            guild_name = content(ctx)

            if guild_name == '':
                guild = ctx.guild
            else:
                for g in bot.guilds:
                    if g.name == guild_name:
                        guild = g
                        break
                else:
                    await ctx.send(f'Servidor {guild_name} nao foi encontrado')
                    return

            to_send = f'Total: {len(guild.members)}\n\n'
            for member in guild.members:
                to_send += f'{member.name}\n'
            await ctx.send(to_send)

        @self.command(pass_context=True)
        async def rerank(ctx):
            if ctx.author.id == self.master_id:
                threshold = 0.6
                ct = content(ctx)
                members = ctx.guild.members
                members_name = [member.name for member in members]
                ration, mem = list_similar(ct, members_name, anime_b=True)
                print(ration)
                if ration > threshold:
                    for member in members:
                        if member.name == mem:
                            rank = shelve.open(f'{self.path}/database/rank/rank')
                            mem_id = str(member.id)
                            if str(member.id) not in list(rank.keys()):
                                await ctx.send('esse usuario nao eh um Rrankerrr ainda')
                            else:
                                rank[mem_id] = 0
                            rank.close()
            else:
                await ctx.send('NAO')

        @self.command(pass_context=True)
        async def planos(ctx, plano_n: int = None):
            res = requests.get('https://starwebfibra.com.br/planos-de-internet/', headers=self.headers)
            res.raise_for_status()
            soup = bs4.BeautifulSoup(res.text, "html.parser")
            # with open('teste.html', 'w') as file:
            #     file.write(res.text)
            soup = soup.find('div', class_="row_col_wrap_12 col span_12 dark left")
            planos = soup.find_all('div', class_='vc_column-inner')

            if plano_n:
                if plano_n > len(planos):
                    await ctx.send('eles n tem essa quantidade de planos')
                elif plano_n < 0:
                    await ctx.send('vc ta me zoando? eh isso?')
                else:
                    for idx, plano in enumerate(planos):
                        du = plano.find('div', class_='wpb_wrapper').text
                        du = [s for s in du.split() if s.isdigit()]

                        download = du[1]
                        upload = du[2]
                        preco = plano.find('h2').text.replace(' ', '')
                        stats = f'Download = {download}Mbps\n' \
                                f'Upload      = {upload}Mbps\n' \
                                f'Preço         = {preco}'
                        if idx + 1 == plano_n:
                            await ctx.send(f'Plano {plano_n}:\n{stats}')
            else:
                await ctx.send(f'starweb tem {len(planos)} planos')

        @self.command(pass_context=True)
        async def help(ctx):
            embed = discord.Embed(color=discord.Color.orange())
            embed.set_author(name='Comandos (* significa opcional):')
            embed.add_field(name='Tem q ta num canal de voz:',
                            value='**set_music** - configura o canal de texto para tocar musica apenas com o link '
                                  'ou nome (recomendado criar um canal de texto especifico)\n'
                                  '**remove_music** - remove o canal da lista\n'
                                  '**play (URL)** - toca musica pelo link ou pesquisa por ela\n'
                                  '**live (URL)** - toca a musica de uma live do yt\n'
                                  '**skip** - pula a musica\n'
                                  '**pause** - pausa a musica\n'
                                  '**resume** - resume a musica\n'
                                  '**join** - entra no canal\n'
                                  '**leave** - sai do canal\n'
                                  '**spasm (vezes)** - da gatinho esse\n '
                                  '**t (frase)** - eu sei falar sabia? pra mudar a lingua eh so '
                                  'colocar "!" e a lingua na frente (lista em langs)\n'
                                  '**sb (arquivo) (vezes*)** - toca o soundboard\n'
                                  '**sbfiles** - lista de tds os arquivos do soundboards\n'
                                  '**sbsave (arquivo)** - salva pra sua lista pessoal\n'
                                  '**sbremove (arquivo)** - remove ele da lista\n'
                                  '**sbmy** - mostra a sua lista\n'
                                  '**sbrecommended** - mostra os arquivos recomendados por mim (e meu mestre)\n'
                                  '**entrar (canal)** - coloque o nome do canal de voz q o bot '
                                  'entra la'
                                  '', inline=False)

            embed.add_field(name='Anime (site: https://nyaa.si/?f=2&c=1_2&q=):',
                            value='**set_anime** - seta canal para avisa quando um ep novo do anime sai\n'
                                  '**my_anime** - lista dos animes q o bot esta observando\n'
                                  '**add_anime (anime)** - adiciona o anime pre avisar o proximo ep\n'
                                  '**remove_anime (anime)** - remove o anime da lista\n'
                                  '**clear_anime** - limpar td a sua lista (final de season)\n'
                                  '**hiragana** - aprenda a lingua chamada anime\n'
                                  '**katakana** - aprenda a lingua chamada anime^2\n'
                                  '', inline=False)

            embed.add_field(name='Comandos q mudam a frase:',
                            value='**Aa (frase)** - deixa a frase mais engracada\n'
                                  '**morse (frase)** - transforma a frase em morse ou morse em frase\n'
                                  '**say (frase)** - ele so repete\n'
                                  '**time (nomes)** - so colocar os nomes separados por espaco e '
                                  'o bot embaralha, bom pra tira time'
                                  '', inline=False)

            embed.add_field(name='Jogos:',
                            value='**joguinho** - cuidado que eh perigoso\n'
                                  '**helpjogo** - guia para troxas de como joga o joguinho perigoso\n'
                                  '**leaderboard** - mostra os que mais foram longe no joguinho\n'
                                  '**joguinho2 (@)** - joguinho 2, chama outra pessoa pra jogar tbm\n'
                                  '**r (dados)D(lados)+(extra*)** - ex: //r 3D12+2'
                                  '', inline=False)

            embed.add_field(name='Zoeiras com alguem:',
                            value='**herele** - HEREEEEEEEEEEEEEEEEEELE\n'
                                  '**casar (@)** - pede em casamento a pessoa\n'
                                  '**pp (@)** - kiba a doto de perfil de alguem\n'
                                  '**ban (@)** - bane alguem de usar alguns comandos do bot\n'
                                  '**unban (@)** - da mais uma chance pro cara vai\n'
                                  '**ban_list** - list dos humilhados\n'
                                  '**channel_ban (@)** - bane a pessoa de entrar em algum canal de voz\n'
                                  '**channel_unban (@)** - le o ultimo comando\n'
                                  '**channel_ban_list** - le o penultimo comando burro\n'
                                  '**mute (@)** - serve pra muta alguem\n'
                                  '**unmute (@)** - serve pra desmuta alguem\n'
                                  '**jaula (@)** - manda o cara pra jaaaaaaaaaula\n'
                                  '**limar (@)** - longa historia\n'
                                  '**limpar (@) (y)** - limpa as mensagens do cara chato entre as '
                                  'y mensagens anteriores\n'
                                  '**i2a (url ou imagem anexada)** - (Image to Ascii) transforma a imagem em ascii\n'
                                  '', inline=False)

            embed.add_field(name='Economia (WIP):',
                            value='**create_account** - cria uma conta bancaria no meu'
                                  ' banco totalmente seguro\n'
                                  '**wallet** - quanto dinheiro voce tem na frente de todo mundo, oq'
                                  ' poderia dar errado?\n'
                                  '**add**\n'
                                  '**reset**\n'
                                  '**reset_user**\n'
                                  '', inline=False)

            embed.add_field(name='Vigiar:',
                            value='**set_discount** - ele seta o canal de texto e avisa qnd tiver uma '
                                  'promocao de 100% em um jogo (to orgulhoso desse)\n'
                                  '**remove_discount** - tira o canal da lista\n'
                                  '**set_crackwatch** - seta o canal para avisar os jogos novos q foram crackeados\n'
                                  '**remove_crackwatch** - tira o canal\n'
                                  '', inline=False)

            embed.add_field(name='Paz (ultrapassado):',
                            value='**manu** - muta a cantoria dela\n'
                                  '', inline=False)

            embed.add_field(name='Listas:',
                            value='**langs** - lista de todas as linguas que a funcao tts reconhece\n'
                                  '', inline=False)

            embed.add_field(name='Diversos:',
                            value='**ran_sub (subreddit)** - um post aleatorio\n'
                                  '**set_hino (horario) (url)** - horario tem q ser no formato 15:30 por '
                                  'exemplo\n'
                                  '**ver_hinos** - horario e nome da lista de hinos\n'
                                  '**apagar_hino (hino)** - coloque o nome do hino e ele eh apagado\n'
                                  '**temp (cidade)** - temperatura\n'
                                  '**clima (cidade)** - TUDO da cidade\n'
                                  '**rank** - mostra o rank das pessoas, pd marca alguem pra ver o dela\n'
                                  '**panela** - panela60\n'
                                  '**todos_panela** - deixa td mundo do server com o nick daora (cuidado)\n'
                                  '**kill** - se td der errado, mata ele (se usar eu vo atras de vc)\n'
                                  '**dolar** - ta caro\n'
                                  '**euro** - foda bixo\n'
                                  '**russo** - pra vc quer sbr do dinheiro da russia?\n'
                                  '**bit** - (bitcoin) ta mais caro\n'
                                  '**dodge** - (dodgecoin) esse eu consigo compra\n'
                                  '**planos** - planos da starweb'
                                  '**help** - tu eh burro cara\n'
                                  '', inline=False)

            embed.add_field(name='Debugging:',
                            value='**logger_on** - se um membro comum usar qlqr um desses comandos ele vai '
                                  'pra jaula sem do, isso sao ferramentas do dev troxa q n sb programa\n'
                                  '**fix_music_messages**\n'
                                  '**logger_off**\n'
                                  '**download**\n'
                                  '**guilds**\n'
                                  '**voice_channels**\n'
                                  '**text_channels**\n'
                                  '**members**\n'
                                  '**baixar**\n'
                                  '**rerank**\n'
                                  '', inline=False)
            await ctx.send(embed=embed)

        @self.command(pass_context=True)
        async def langs(ctx):
            def chunks(lst, n):
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]

            embed = discord.Embed(color=discord.Color.blue())
            embed.set_author(name='Linguas')

            languages_dict = gtts.lang.tts_langs()
            languages = []
            for thing in languages_dict:
                languages.append(f'{thing}: {languages_dict[thing]}')
            lists = list(chunks(languages, 39))
            for lst in lists:
                temp = ''
                for element in lst:
                    temp += element + '\n'
                embed.add_field(name='possiveis linguas:', value=temp, inline=False)
            await ctx.send(embed=embed)

        @self.command(pass_context=True)
        async def manu(ctx):
            await ctx.message.delete()
            manu_id = 277996927679856640
            for channel_v in ctx.message.guild.voice_channels:
                for thing in channel_v.members:
                    if thing.id == manu_id:
                        await thing.edit(mute=True)
                        await thing.edit()

    async def discount(self):
        def check(list1, list2):
            contain = True
            for thing in list1:
                if thing in list2:
                    contain = False
            return contain

        subreddit = await self.reddit.subreddit('GameDeals')
        new = subreddit.new(limit=50)
        storage = shelve.open(f'{self.path}/database/storage/storage')
        blacklist = ['indiegala', 'godankey', 'games2gether', 'itch.io']
        try:
            track = storage['list']
        except:
            track = []

        async for post in new:
            if check(blacklist, post.title.lower().replace(' ', '')):
                if '100%' in post.title and post.title not in track:
                    for key in list(storage.keys()):
                        if key != 'list':
                            channel_id = storage[key]
                            channel = bot.get_channel(channel_id)
                            history = await channel.history(limit=10).flatten()
                            history2 = []
                            for i in history:
                                history2.append(i.content.split('\n')[0])
                            if post.title not in history2:
                                if key != str(channel.guild):
                                    del storage[key]
                                    storage[str(channel.guild)] = channel_id
                                await channel.send(f"{post.title}\nPosted by: **{post.author}**\n"
                                                   f"https://www.reddit.com/{post.id}")
                            else:
                                print("fui transferido de maquina")

                    track.append(post.title)
                    if len(track) >= 10:
                        track.remove(track[0])

        storage['list'] = track
        storage.close()

        await asyncio.sleep(3600)
        await self.discount()

    async def anthem(self):
        hinos = shelve.open(f'{self.path}/database/hinos/hinos')
        for key in list(hinos.keys()):
            server = bot.get_guild(int(key[4:]))
            hour_prog = int(key[0:2])
            minute_prog = int(key[2:4])
            hour_now = datetime.now().hour
            minute_now = datetime.now().minute

            print('tentei')
            if hour_now == hour_prog and minute_now == minute_prog:
                file = hinos[key]
                channel, people = get_people(server)
                print(f"chosen channel = {channel}")
                if people:
                    voice = get(bot.voice_clients, guild=server)
                    if voice:
                        if voice.is_playing():
                            await voice.stop()
                        if voice.is_connected():
                            await voice.disconnect()
                    voice = await channel.connect()

                    voice.play(discord.FFmpegPCMAudio(f'{self.path}/database/hinos/{file}.mp3'))
                    voice.source = discord.PCMVolumeTransformer(voice.source)
                    voice.source.volume = self.volume
                else:
                    await bot.get_channel(745999056836231229).send(
                        f"Ngm veio prestar respeito ao hino: {hinos[key]}, da próxima vez eu vo usa o {self.P}bomba")

        hinos.close()
        await asyncio.sleep(30)
        await self.anthem()

    async def anime(self):
        threshold = 0.6
        res = requests.get('https://nyaa.si/?f=2&c=1_2&q=', headers=self.headers)
        res.raise_for_status()

        soup = bs4.BeautifulSoup(res.text, "html.parser")
        soup = soup.find_all('tr', class_="success")

        animes_guild = shelve.open(f'{self.path}/database/animes/animes_guild')
        animes_list = shelve.open(f'{self.path}/database/animes/animes_list')
        track_list = shelve.open(f'{self.path}/database/animes/animes_track')
        animes_check = []
        for key in list(animes_list.keys()):
            for anime_in_list in animes_list[key]:
                if anime_in_list not in animes_check and list_similar(anime_in_list, animes_check) < threshold:
                    animes_check.append(anime_in_list.lower())

        for anime_ep in soup:
            a = anime_ep.find('a', href=True, text=True)
            title = a.text
            link = f"https://nyaa.si{a['href']}"

            if '1080p' in title.lower():
                num, anime_name = list_similar(title.lower().split('] ')[1].rsplit('-', 1)[0], animes_check, True)
                if list_similar(anime_name, list(track_list.keys())) < threshold:
                    track_list[anime_name] = 0
                if num > threshold or in_in_list(title, animes_check):
                    display_title = title.split('] ')[1]
                    if '(' in display_title:
                        display_title = display_title.split(' (')[0]
                    else:
                        display_title = display_title.split(' [')[0]
                    ep_num = display_title.rsplit('- ', 1)[1]
                    try:
                        ep_num = int(ep_num)
                    except:
                        ep_num = -1
                    if ep_num > track_list[anime_name]:
                        track_list[anime_name] = ep_num
                        mentions = ''
                        for user in list(animes_list.keys()):
                            if list_similar(anime_name, animes_list[user]) > threshold:
                                user = bot.get_user(int(user))
                                mentions += f'{user.mention} '

                        for guild_id in list(animes_guild.keys()):
                            channel_id = animes_guild[guild_id]
                            channel = bot.get_channel(channel_id)
                            await channel.send(f'{mentions}\n{display_title}\n{link}')

        animes_guild.close()
        animes_list.close()
        track_list.close()
        await asyncio.sleep(300)
        await self.anime()

    async def crackwatch(self):
        crack = shelve.open(f'{self.path}/database/crackwatch/crackwatch')
        crack_keys = list(crack.keys())
        if 'track' not in crack_keys:
            track = []
        else:
            track = crack['track']
        crack_url = 'https://api.crackwatch.com/api/games?page=0&sort_by=crack_date&is_cracked=true'
        req = requests.get(crack_url)
        json_list = req.json()[:10]
        json_list.reverse()
        for game in json_list:
            if game['_id'] not in track:
                for key in crack_keys:
                    if key != 'track':
                        channel = bot.get_channel(crack[key])
                        await channel.send(f'Game: {game["title"]}\n'
                                           f'Protections: {game["protections"]}\n'
                                           f'Groups: {game["groups"]}\n'
                                           f'{game["url"]}\n')
                        await channel.send(f'{game["image"]}')
                        track.append(game['_id'])

        if len(track) > 15:
            track.remove(track[0])
        crack['track'] = track
        crack.close()
        await asyncio.sleep(3600)
        await self.crackwatch()

    async def starweb(self):
        storage = shelve.open(f'{self.path}/database/random/random')
        res = requests.get('https://starwebfibra.com.br/planos-de-internet/', headers=self.headers)
        res.raise_for_status()

        soup = bs4.BeautifulSoup(res.text, "html.parser")
        soup = soup.find('div', class_="row_col_wrap_12 col span_12 dark left")
        planos = soup.find_all('div', class_='vc_column-inner')
        for idx, plano in enumerate(planos):
            du = plano.find('div', class_='wpb_wrapper').text
            du = [s for s in du.split() if s.isdigit()]

            download = du[1]
            upload = du[2]
            preco = plano.find('h2').text.replace(' ', '')
            stats = f'Download = {download}Mbps\n' \
                    f'Upload      = {upload}Mbps\n' \
                    f'Preço         = {preco}'

            keys = storage.keys()
            if f'plano_{idx}' not in keys:
                storage[f'plano_{idx}'] = [download, upload, preco]
                await bot.get_channel(338441688840142850).send(f'PLANO NOVO:\n{stats}')
            elif [download, upload, preco] != storage[f'plano_{idx}']:
                storage[f'plano_{idx}'] = [download, upload, preco]
                await bot.get_channel(338441688840142850).send(f'STARWEB TROCO DE PLANO DNV\n{stats}')

        storage.close()
        await asyncio.sleep(3600)
        await self.starweb()

    async def music_embed_update(self, info, guild_id):
        q = ''
        for i, music in enumerate(self.queue[guild_id][1:]):
            q += f'{i + 1}: {music[1]}\n'

        if q == '':
            q = 'Empty\n'

        embed = discord.Embed(title=f'Now: {info["title"]}', description=f'Queue:\n{q}\n'
                                                                         f'Send a link to queue',
                              url=self.queue[guild_id][0][0],
                              color=discord.Color.red())
        embed.set_thumbnail(url=info['thumbnail'])

        return embed

    async def usb(self, data):  # WIP
        def after():
            self.playing = False

        self.playing = False
        try:
            if data == 0:
                for guild in self.guilds:
                    for voice_channel in guild.voice_channels:
                        for member in voice_channel.members:
                            if member.id == self.master_id:
                                print(f'entering {voice_channel.name}')
                                await bot.all_commands['join'](None, voice_channel)
                                print('after entering')
            elif data == 1:
                if not self.playing:
                    self.playing = True
                    print('banido')
                    voice = get(bot.voice_clients, guild=self.get_guild(338441688840142850))
                    if voice is not None:
                        voice.play(discord.FFmpegPCMAudio(f'{self.path}/soundboard/banido.mp3'),
                                   after=after())
                        voice.source = discord.PCMVolumeTransformer(voice.source)
                        voice.source.volume = self.volume
                    else:
                        self.playing = False
            elif data == 2:
                if not self.playing:
                    self.playing = True
                    print('return-monke')
                    voice = get(bot.voice_clients, guild=self.get_guild(338441688840142850))
                    if voice is not None:
                        voice.play(discord.FFmpegPCMAudio(f'{self.path}/soundboard/return-monke.mp3'),
                                   after=after())
                        voice.source = discord.PCMVolumeTransformer(voice.source)
                        voice.source.volume = self.volume
                    else:
                        self.playing = False
            elif data == 3:
                if not self.playing:
                    self.playing = True
                    print('rporta')
                    voice = get(bot.voice_clients, guild=self.get_guild(338441688840142850))
                    if voice is not None:
                        voice.play(discord.FFmpegPCMAudio(f'{self.path}/soundboard/rporta.mp3'),
                                   after=after())
                        voice.source = discord.PCMVolumeTransformer(voice.source)
                        voice.source.volume = self.volume
                    else:
                        self.playing = False
            elif data == 4:
                if not self.playing:
                    self.playing = True
                    print('nhaaum')
                    voice = get(bot.voice_clients, guild=self.get_guild(338441688840142850))
                    if voice is not None:
                        voice.play(discord.FFmpegPCMAudio(f'{self.path}/soundboard/nhaaum.mp3'),
                                   after=after())
                        voice.source = discord.PCMVolumeTransformer(voice.source)
                        voice.source.volume = self.volume * 1.5
                    else:
                        self.playing = False
        except Exception as e:
            print('coulndt play audio via usb, probably already playing')
            print(e)

    def remove_old_songs(self):  # obsolete
        q = os.listdir(f"{self.path}/music/queue")
        if len(q) > 1:
            for song in q:
                if song != 'waiting.opus':
                    os.remove(f"{self.path}/music/queue/{song}")

    @staticmethod
    async def send(channel, text):
        await channel.send(text)

    @staticmethod
    def music_embed_idle():
        embed = discord.Embed(title='Controller', description=f'Currently not playing...\n\n'
                                                              f'Send a link to play',
                              color=discord.Color.red())
        embed.set_thumbnail(
            url='https://64.media.tumblr.com/2b4fd10ad6a54af25605a764775943ae/tumblr_pndzvk9ESR1xn70plo1_400.jpg')

        return embed


class user_banned(Exception):
    """used when a banned user tries to use a command"""
    pass


def is_safe():  # decorator for checking if text channel is NSFW
    def pred(func):
        @functools.wraps(func)
        async def check(*args, **kwargs):
            ctx = args[0]
            if ctx.message.channel.is_nsfw():
                return await func(*args, **kwargs)
            else:
                return await bot.send(ctx.message.channel, 'NAAAAO PODE, TO AVISANDO')

        return check

    return pred


def usb():
    usb = Serial('com4', baudrate=115200)

    while True:
        uncoded_data = usb.readline()
        data = str(uncoded_data[0:len(uncoded_data)].decode('utf-8'))
        choice = int(data[:1])
        asyncio.run(bot.usb(choice))


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def list_similar(a, lista, anime_b=False):
    a = a.lower()
    bigger = 0
    anime = ''
    for element in lista:
        sim = similar(a, element.lower())
        if sim > bigger:
            bigger = sim
            anime = element
    if anime_b:
        return bigger, anime
    else:
        return bigger


def in_in_list(a, lista):
    for element in lista:
        if a.lower() in element.lower() or element.lower() in a.lower():
            return True
    return False


def get_people(server, debug=True):
    last_counter = 0
    anthem_channel = None
    anthem_people = False
    for channelV in server.voice_channels:
        if debug:
            print(f"voice channel = {channelV}, number of members = {len(channelV.members)}")
        counter = len(channelV.members)

        if counter > last_counter:
            anthem_channel = channelV
            anthem_people = True
            last_counter = counter
    return anthem_channel, anthem_people


def content(ctx):
    try:
        message = ctx.content
        return message
    except:
        message = ctx.message.content

    if message.count(" ") > 0:
        return message.split(" ", 1)[1]
    else:
        return ''


def foo(s):
    ret = ""
    i = True
    for char in s:
        if i:
            ret += char.upper()
        else:
            ret += char.lower()
        if char != ' ':
            i = not i
    return ret


def encrypt(message):
    cipher = ''
    for letter in message:
        if letter != ' ':
            cipher += bot.MORSE_CODE_DICT[letter] + ' '
        else:

            cipher += ' '

    return cipher


def decrypt(message):
    message += ' '
    i = 0
    decipher = ''
    citext = ''
    for letter in message:

        if letter != ' ':
            i = 0
            citext += letter
        else:
            i += 1
            if i == 2:
                decipher += ' '
            else:
                decipher += list(bot.MORSE_CODE_DICT.keys())[list(bot.MORSE_CODE_DICT.values()).index(citext)]
                citext = ''

    return decipher


def download_song(url):
    path = bot.path
    queue = len(os.listdir(f"{path}/music/queue"))
    queue_path = f"{path}/music/queue/song{queue}.%(ext)s"
    os.system(f'youtube-dl -o "{queue_path}" -x {url}')


def start_presence():
    CLIENT_ID = 000  # credencial

    print('Trying to initialize Rich Presence...')
    while True:
        try:
            prp = pypresence.Presence(CLIENT_ID)
            prp.connect()
            prp.update(
                details='Alimentando o Escravo',
                state='Programando',
                large_image='laila_pfp',
                small_image='pycharm_icon',
                large_text='Laila',
                small_text='PyCharm',
                start=int(time.time()),
                party_size=[1, 2],
                buttons=[{"label": "Adicionar ao Server",
                          "url": "https://discord.com/api/oauth2/authorize?client_id=757795510357590148&permissions=8&scope=bot"},
                         {"label": "OwO", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}]
            )
            print('Rich Presence successfully connected!')
            break
        except pypresence.exceptions.InvalidPipe:
            print('attempt failed, trying again in 10 seconds...')
            time.sleep(10)


if __name__ == '__main__':
    start_presence()
    print('initializing bot...')
    bot = MyBot(command_prefix="//", intents=discord.Intents.all(), self_bot=False)
    # bot.run('xxx')  # bot de teste  # credencial
    # bot.start('xxx')  # credencial
    bot.run('xxx')  # bot normal  # credencial
