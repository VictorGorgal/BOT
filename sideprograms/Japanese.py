from random import choice
from operator import itemgetter
from math import floor


class japanese:
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.track_total = {}
        self.track_correct = {}
        self.track_used = {}
        self.hiragana = {  # dicionario contendo o hiragana
            'ka': 'か', 'sa': 'さ', 'ta': 'た',
            'na': 'な', 'ha': 'は', 'ma': 'ま',
            'ya': 'や', 'ra': 'ら', 'wa': 'わ',
            'ga': 'が', 'za': 'ざ', 'da': 'だ',
            'ba': 'ば', 'pa': 'ぱ', 'a': 'あ',

            'ki': 'き', 'shi': 'し', 'chi': 'ち',
            'ni': 'に', 'hi': 'ひ', 'mi': 'み',
            'ri': 'り', 'gi': 'ぎ', 'ji': 'じ',
            'dji': 'ぢ', 'bi': 'び', 'pi': 'ぴ',
            'i': 'い',

            'ku': 'く', 'su': 'す', 'tsu': 'つ',
            'nu': 'ぬ', 'fu': 'ふ', 'mu': 'む',
            'yu': 'ゆ', 'ru': 'る', 'gu': 'ぐ',
            'zu': 'ず', 'dzu': 'づ', 'bu': 'ぶ',
            'pu': 'ぷ', 'u': 'う',

            'ke': 'け', 'se': 'せ', 'te': 'て',
            'ne': 'ね', 'he': 'へ', 'me': 'め',
            're': 'れ', 'ge': 'げ', 'ze': 'ぜ',
            'de': 'で', 'be': 'べ', 'pe': 'ぺ',
            'e': 'え',

            'ko': 'こ', 'so': 'そ', 'to': 'と',
            'no': 'の', 'ho': 'ほ', 'mo': 'も',
            'yo': 'よ', 'ro': 'ろ', 'wo': 'を',
            'n': 'ん', 'go': 'ご', 'zo': 'ぞ',
            'do': 'ど', 'bo': 'ぼ', 'po': 'ぽ',
            'o': 'お',
        }
        self.katakana = {  # dicionario contendo o katakana
            'ka': 'カ', 'sa': 'サ', 'ta': 'タ',
            'na': 'ナ', 'ha': 'ハ', 'ma': 'マ',
            'ya': 'ヤ', 'ra': 'ラ', 'wa': 'ワ',
            'ga': 'ガ', 'za': 'ザ', 'da': 'ダ',
            'ba': 'バ', 'pa': 'パ', 'a': 'ア',

            'ki': 'キ', 'shi': 'シ', 'chi': 'チ',
            'ni': 'ニ', 'hi': 'ヒ', 'mi': 'ミ',
            'ri': 'リ', 'gi': 'ギ', 'ji': 'ジ',
            'dji': 'ヂ', 'bi': 'ビ', 'pi': 'ピ',
            'i': 'イ',

            'ku': 'ク', 'su': 'ス', 'tsu': 'ツ',
            'nu': 'ヌ', 'fu': 'フ', 'mu': 'ム',
            'yu': 'ユ', 'ru': 'ル', 'gu': 'グ',
            'zu': 'ズ', 'dzu': 'ヅ', 'bu': 'ブ',
            'pu': 'プ', 'u': 'ウ',

            'ke': 'ケ', 'se': 'セ', 'te': 'テ',
            'ne': 'ネ', 'he': 'ヘ', 'me': 'メ',
            're': 'レ', 'ge': 'ゲ', 'ze': 'ゼ',
            'de': 'デ', 'be': 'ベ', 'pe': 'ペ',
            'e': 'エ',

            'ko': 'コ', 'so': 'ソ', 'to': 'ト',
            'no': 'ノ', 'ho': 'ホ', 'mo': 'モ',
            'yo': 'ヨ', 'ro': 'ロ', 'wo': 'ヲ',
            'n': 'ン', 'go': 'ゴ', 'zo': 'ゾ',
            'do': 'ド', 'bo': 'ボ', 'po': 'ポ',
            'o': 'オ',

            'va': 'ヴァ', 've': 'ヴェ', 'vi': 'ヴィ',
            'vo': 'ヴォ', 'vu': 'ヴ',
        }
        self.last_answer = None
        self.kana = None

    def random_hiragana(self):  # escolhe um hiragana aleatorio
        answer = choice(list(self.hiragana))
        self.kana = self.hiragana[answer]
        self.last_answer = answer
        return self.kana

    def random_katakana(self):  # escolhe um katakana aleatorio
        answer = choice(list(self.katakana))
        self.kana = self.katakana[answer]
        self.last_answer = answer
        return self.kana

    def check_answer(self, answer):  # verifica se a resposta esta correta
        self.save_kana()
        if answer.lower().strip() == self.last_answer:
            self.track_correct[f'{self.kana}'] += 1
            return 'Correct'
        else:
            return f'Wrong, it was {self.last_answer}'

    def save_kana(self):  # salva o caracter escolhido para comparar com a resposta dada
        if self.kana not in self.track_used.keys():
            self.track_used[self.kana] = self.last_answer
        if self.kana not in self.track_correct.keys():
            self.track_correct[self.kana] = 0
        if self.kana not in self.track_total.keys():
            self.track_total[self.kana] = 0
        self.track_total[self.kana] += 1

    def stats(self):
        # retorna a porcentagem de acerto junto com o numero total mostrado para
        # cada caracter separado
        to_send = ''
        over_all_correct = 0
        over_all_total = 0
        track_percentage = {}
        for key in self.track_total.keys():
            if self.track_total[key] == 0:
                percentage = 0
            else:
                over_all_correct += self.track_correct[key]
                over_all_total += self.track_total[key]
                percentage = self.track_correct[key] / self.track_total[key] * 100
            track_percentage[key] = floor(percentage * 100)/100.0

        track_percentage = dict(sorted(track_percentage.items(), key=itemgetter(1), reverse=True))
        for key in track_percentage:
            percentage = track_percentage[key]
            to_send += f'{key}({self.track_used[key]}):{" "*5}{self.track_correct[key]}/{self.track_total[key]}{" "*5}{percentage}%\n'

        percentage = over_all_correct / over_all_total * 100
        to_send += f'\nover all:{" "*5}{over_all_correct}/{over_all_total}{" "*5}{percentage:.2f}%'
        return to_send


if __name__ == '__main__':
    c = input('Insira [H] para Hiragana e [K] para Katakana: ').lower()
    j = japanese(None)
    if c == 'h':
        while True:
            print(j.random_hiragana())
            answer = input('Hiragana: ')
            print(j.check_answer(answer))
    elif c == 'k':
        while True:
            print(j.random_katakana())
            answer = input('Katakana: ')
            print(j.check_answer(answer))
    else:
        print('Insira uma opcao valida')
