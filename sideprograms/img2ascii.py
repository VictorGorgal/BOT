import cv2


def img2ascii(img):
    LIGHT = ['⠀', '░', '▒', '▓', '█']  # niveis de luminozidade diferentes

    if type(img) == str:
        img = cv2.imread(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.resize(img, (100, 100))  # muda o tamanho da imagem para 100x100px

    new = ''
    for x in range(0, 100, 2):  # faz a media do 2 pixeis e substituindo por um dos caracteres de luminozidade
        x1 = img[x]
        x2 = img[x+1]
        for y in range(100):
            new += LIGHT[round((round(x1[y] / 63.5) + round(x2[y] / 63.5)) / 2)]
        new += '\n'

    return new  # retorna a string contendo a foto em caracteres ascii


if __name__ == '__main__':
    from requests import get
    from numpy import frombuffer, uint8

    print('sugestao https://cdn.discordapp.com/attachments/465336993853734914/912865849747079188/35df97c0ad12bd17c08d7957b3aa74c6.webp')
    img = input('Insira a URL de uma imagem: ')
    if type(img) == str:
        pic = get(img)
        if pic.ok:
            img = cv2.imdecode(frombuffer(pic.content, uint8), -1)

    print(img2ascii(img))
