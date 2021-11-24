from random import randint


class TicTacToe:
    def __init__(self, d1=None, d2=None):
        self.game = [[" - ", " - ", " - "],
                     [" - ", " - ", " - "],
                     [" - ", " - ", " - "]]
        self.running = True
        self.player1 = bool(randint(0, 1))
        self.x = None
        self.y = None
        self.discordPlayer1 = d1
        self.discordPlayer2 = d2

    def set_message(self, message):
        self.message = message

    def get_playing_name(self):
        if self.player1:
            return self.discordPlayer1.name
        else:
            return self.discordPlayer2.name

    def playing(self, name):
        if self.player1:
            if name == self.discordPlayer1.name:
                return True
        else:
            if name == self.discordPlayer2.name:
                return True
        return False

    def valid_inputs(self, message):
        new = list(message.upper())
        if new[0] in ['Q', 'W', 'E'] and new[1] in ['1', '2', '3']:
            return True
        else:
            return False

    def draw(self, emojy=False):  # desenha o estado atual do quadro
        if emojy:
            message = "       1     2     3\n"
            a = ["Q ", "W", "E  "]
            for n, row in zip(a, self.game):
                message += f"{n} "
                for column in row:
                    if column == ' - ':
                        message += ':blue_square: '
                    elif column == ' X ':
                        message += ':regional_indicator_x: '
                    else:
                        message += ':regional_indicator_o: '
                message += '\n'
            return message
        else:
            message = "   1  2  3\n"
            a = ["Q", "W", "E"]
            for n, row in zip(a, self.game):
                message += f"{n} "
                for column in row:
                    message += column
                message += '\n'
            return message

    def win(self, winner):  # mostra qual jogador ganhou
        self.draw()
        self.running = False
        message = "-" * 20 + '\n'
        if self.discordPlayer1 is None:
            message += f"{winner} GANHOU!!!\n"
        else:
            message += f"{self.discordPlayer1.name if winner == ' X ' else self.discordPlayer2.name} GANHOU!!!\n"
        message += "-" * 20
        return message

    def gamedraw(self):  # mostra se deu velha
        self.draw()
        self.running = False
        return "Deu velha"

    def check(self):  # verifica se algum jogador ganhou ou se deu velha
        for i in range(len(self.game)):
            if self.game[i][0] == self.game[i][1] == self.game[i][2] and self.game[i][0] != " - ":
                return self.win(self.game[i][0])

            if self.game[0][i] == self.game[1][i] == self.game[2][i] and self.game[0][i] != " - ":
                return self.win(self.game[0][i])

            if self.game[0][0] == self.game[1][1] == self.game[2][2] and self.game[0][0] != " - ":
                return self.win(self.game[0][0])

            if self.game[0][2] == self.game[1][1] == self.game[2][0] and self.game[0][2] != " - ":
                return self.win(self.game[0][2])
        self.frase = ""
        for lista in self.game:
            self.frase += "".join(lista)
        if "-" not in self.frase:
            return self.gamedraw()


if __name__ == '__main__':
    tic_tac_toe = TicTacToe()

    while tic_tac_toe.running:
        print(tic_tac_toe.draw())
        tic_tac_toe.player1 = not tic_tac_toe.player1
        played = list(input(f"player {1 if tic_tac_toe.player1 else 2} input: ").upper().replace("Q", "1")
                      .replace("W", "2").replace("E", "3"))
        tic_tac_toe.x = int(played[1]) - 1
        tic_tac_toe.y = int(played[0]) - 1
        if tic_tac_toe.game[tic_tac_toe.y][tic_tac_toe.x] == " - ":
            tic_tac_toe.game[tic_tac_toe.y][tic_tac_toe.x] = " X " if tic_tac_toe.player1 else " O "
        else:
            print("o lugar ja foi marcado")
            tic_tac_toe.player1 = not tic_tac_toe.player1
        print(tic_tac_toe.check())
