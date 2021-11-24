from datetime import datetime
from os import path, mkdir
from io import open


class logger:
    def __init__(self, path, active=True):
        self.PATH = path
        self.active = active

    def on(self):
        self.active = True

    def off(self):
        self.active = False

    @staticmethod
    def get_time():
        when = datetime.now()
        return f'@{when.hour}:{when.minute}:{when.second} | {when.day}/{when.month}/{when.year}'

    def write_log(self, guild, file, text):
        print(text)
        if self.active:
            if not path.isdir(f'{self.PATH}/log/{guild}'):
                mkdir(f'{self.PATH}/log/{guild}')
            with open(f'{self.PATH}/log/{guild}/{file}.txt', 'a', encoding='utf-8') as file:
                file.write(text + '\n')

    def log_message(self, ctx):
        time = self.get_time()

        guild_name = ctx.guild.name
        guild_id = ctx.guild.id
        channel = ctx.channel.name
        author = ctx.author.name
        content1 = ctx.content
        content2 = [x.url for x in ctx.attachments]

        text = f'MESSAGE {time} {guild_name} >> {channel} > {author} said: {content1}'
        if content2:
            text += f' > attachment: {content2}'

        self.write_log(guild_id, channel, text)

    def log_voice(self, member, before, after):
        time = self.get_time()

        guild_name = member.guild.name
        guild_id = member.guild.id
        text = ''

        if not before.channel:
            text = f'VOICE {time} {guild_name} >> {member.name} > entered > {after.channel.name}'
        elif not after.channel:
            text = f'VOICE {time} {guild_name} >> {member.name} > left > {before.channel.name}'
        elif before.channel.id != after.channel.id:
            text = f'VOICE {time} {guild_name} >> {member.name} > moved to > {after.channel.name}'

        if text != '':
            self.write_log(guild_id, 'VOICE', text)
