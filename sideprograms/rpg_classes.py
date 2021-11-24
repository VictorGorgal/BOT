import random
from math import floor, log
from numpy import maximum


class Battle:
    def __init__(self, player):
        self.player = player
        self.Tafter_killing = True
        self.Tequip = True
        self.Tlevelup_message = True
        self.Tlevelup = True

    def set(self, enemy, message=None):
        self.enemy = enemy
        self.bot_mes = message

    def progress_check(self):
        if self.player.level < 3:
            self.enemy.life = random.randint(20, 50)
            self.enemy.damageMin = 4
            self.enemy.damageMax = 7
            self.XPgain = 5
            self.loot = 1.25
        elif self.player.level < 5:
            self.enemy.life = random.randint(50, 100)
            self.enemy.damageMin = 10
            self.enemy.damageMax = 15
            self.XPgain = 6
            self.loot = 1.75
        elif self.player.level < 10:
            self.enemy.life = random.randint(100, 175)
            self.enemy.damageMin = 15
            self.enemy.damageMax = 20
            self.XPgain = 7
            self.loot = 2.5
        else:
            self.enemy.life = maximum(random.randint(self.player.level * 16, self.player.level * 32),
                                      random.randint(self.player.damage * 16, self.player.damage * 32))
            self.enemy.damageMin = self.player.level * 1.2
            self.enemy.damageMax = self.player.level * 1.8
            self.XPgain = floor(self.player.level * 0.45)
            self.loot = self.player.level * 0.175

    def convert(self, choice):
        if choice == '🇶':
            attack = 'Q'
        elif choice == '🇼':
            attack = 'W'
        elif choice == '🇪':
            attack = 'E'
        elif choice == '🇷':
            attack = 'R'

        elif choice == '🇸':
            attack = 'S'
        elif choice == '🇳':
            attack = 'N'
        elif choice == '🇻':
            attack = 'V'
        elif choice == '🇩':
            attack = 'D'
        else:
            attack = None

        return attack

    def dead(self):
        if self.player.life > 0:
            return False
        else:
            return True

    def won(self):
        if self.enemy.life > 0:
            return False
        else:
            return True

    def attack(self, hability):
        hability = self.convert(hability)
        if self.enemy.burn > 0:
            self.enemy.burn -= 1
            self.enemy.life -= self.player.damage * 0.2

        self.player.mC = 1

        if self.player.cR > 0:
            self.player.cR -= 1

        self.enemy.damage = random.uniform(self.enemy.damageMin, self.enemy.damageMax)

        crit = random.randint(1, 10)
        if crit <= 2:  # 20% de dar dano critico
            self.player.mC = 2

        if hability == "Q":
            self.player.Q(self.enemy)
        elif hability == "W":
            self.player.W(self.enemy)
        elif hability == "E" and self.player.level >= 3:
            self.player.E(self.enemy)
        elif hability == "R" and self.player.level >= 5:
            self.player.R(self.enemy)

        if hability in ['Q', 'W', 'E']:
            self.player.mR = 1

        message = f'{self.enemy.name} = {self.enemy.life:.2f} ({self.enemy.life - self.enemy.lastLife:.2f})\n'
        message += f'Voce = {self.player.life:.2f} ({self.player.life - self.player.lastLife:.2f})'

        self.player.lastLife = self.player.life
        self.enemy.lastLife = self.enemy.life

        return message

    def after_killing(self):
        self.Tafter_killing = False
        self.player.XP += self.player.XPgain
        self.player.drop = random.randint(1, 2)  # drop de espada ou armadura
        self.player.random1 = random.uniform(1, self.player.loot)

        message = f'Fez o {self.enemy.name} deixar de ser troxa! +{self.player.XPgain}XP\n'
        if self.player.drop == 1:
            message += f'Voce encontrou uma espada com um multiplicador de {self.player.random1:.2f}x\n'
            message += f'A sua atual possui {self.player.weapon_multiplyer:.2f}x\n'
        else:
            message += f'Voce encontrou uma armadura com um multiplicador de {self.player.random1:.2f}x\n'
            message += f'A sua atual possui {self.player.armor_multiplyer:.2f}x\n'
        message += 'Deseja trocar?'
        return message

    def equip(self, hability):
        self.Tequip = False
        hability = self.convert(hability)
        if hability == 'S':
            if self.player.drop == 1:
                self.player.weapon_multiplyer = self.player.random1
            else:
                self.player.armor_multiplyer = self.player.random1

    def levelup_message(self):
        self.Tlevelup_message = False
        message = f'XP: {self.player.XP}\n'
        if self.player.XP >= 10:
            self.player.level += 1
            self.player.XP -= 10
            message += f'level up! level atual: {self.player.level}\n'
            message += f'>>>Aumentar a sua vida total em {self.player.life_levelup():.2f}[V]\n'
            message += f'>>>Aumentar seu dano base em {self.player.damage_levelup():.2f}[D]'
            return message

    def levelup(self, hability):
        self.Tlevelup = False
        hability = self.convert(hability)
        if hability == 'V':
            self.player.lifebase += self.player.life_levelup()
            message = f'sua vida base eh de {self.player.lifebase}HP'
        elif hability == 'D':
            self.player.damagebase += self.player.damage_levelup()
            message = f'Seu dano base eh de {self.player.damagebase}'
        else:
            message = ''
        return message

    def level_check(self):
        if self.player.XP >= 10:
            return True
        else:
            return False

    def reset(self):
        self.progress_check()
        self.player.reset()

        ene = random.randint(1, 2)
        if ene == 1:
            self.enemy = Zombie()
        elif ene == 2:
            self.enemy = Skeleton()
        self.progress_check()

        self.Tafter_killing = True
        self.Tequip = True
        self.Tlevelup_message = True
        self.Tlevelup = True

    def to_add(self):
        to_add = ['🇶', '🇼']
        if self.player.level >= 3:
            to_add.append('🇪')
        if self.player.level >= 5:
            if self.player.cR == 0:
                to_add.append('🇷')
            else:
                to_add.append('❌')
        return to_add


class Mage:
    def __init__(self, ctx=None, mes=None):
        self.name = 'Mage'
        self.bot_mes = mes
        self.life_levelup_base = 8
        self.damage_levelup_base = 4
        self.lifebase = 20
        self.level = 1
        self.armor_multiplyer = 1
        self.armorbase = 5
        self.armor = 5
        self.weapon_multiplyer = 1
        self.damagebase = 10
        self.damage = 10
        self.XP = 10
        self.XPgain = 5
        self.loot = 1.25
        self.mC = 1  # multiplier crit
        self.cR = 0  # cooldown R
        self.dealt = 0
        self.mR = 1  # multiplier R
        self.life = self.lifebase
        self.lastLife = self.life
        self.stage = 0
        self.drop = 0
        self.random1 = 0
        if ctx:
            self.user_id = ctx.message.author.id
            self.channel = ctx.message.channel
        else:
            self.user_id = None
            self.channel = None

    def Q(self, enemy):
        self.life -= enemy.damage
        enemy.life -= self.damage * self.mR * self.mC

    def W(self, enemy):
        self.life += (self.lifebase * 0.4) * self.mR * self.mC
        if self.life > self.lifebase:
            self.life = self.lifebase

    def E(self, enemy):
        self.life -= enemy.damage
        enemy.life -= self.damage * 0.8 * self.mR * self.mC
        enemy.burn = 4

    def R(self, enemy):
        self.life -= enemy.damage
        self.mR = 3
        self.cR = 6

    def reset(self):
        self.life = self.lifebase
        self.lastLife = self.life
        self.damage = self.damagebase * self.weapon_multiplyer
        self.armor = self.armorbase * self.armor_multiplyer

    def life_levelup(self):
        return maximum(log(self.level, 1.2), self.life_levelup_base)

    def damage_levelup(self):
        return maximum(log(self.level, 1.2) / 2, self.damage_levelup_base)


class Zombie:
    def __init__(self):
        self.name = 'Zombie'
        self.life = 25
        self.lastLife = self.life
        self.damage = 0
        self.damageMin = 3
        self.damageMax = 6
        self.burn = 0


class Skeleton:
    def __init__(self):
        self.name = 'Skeleton'
        self.life = 25
        self.lastLife = self.life
        self.damage = 0
        self.damageMin = 3
        self.damageMax = 6
        self.burn = 0


if __name__ == '__main__':
    pass
