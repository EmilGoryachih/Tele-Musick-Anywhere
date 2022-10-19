from PIL import Image, ImageDraw, ImageFont
import qrcode
import cv2 as cv
import os


class QR_Operation():
    def __init__(self, qr_name='qr'):
        self.qr_name = qr_name

    def qr_coder(self, text='Pass'): # Никита, что будет здесь? Название или текст?
        img = qrcode.make(text) # при помощи библиотеки qrcode делаем qr из введённого текста
        img.save('pass/' + self.qr_name + '-base.png') # сохраняем

    def im_to_qr(self, image_name='image'):
        im = Image.open(image_name + '.png') # открываем фоновое изображение(предлагаю изображение, привязанное к пользователю)
        im2 = Image.open('pass/' + self.qr_name + '-base.png') # открываем qr
        x, y = im2.size # получаем размер qr для ресайза изображения пользователя
        pixels_qr = im2.load() # получаем список пикселей изображения
        im = im.resize((x, y)) # приводим изображение к одному размеру с qr
        pixels_im = im.load() # получаем список пикселей изображения
        im.putalpha(255)

        for i in range(1, x - 1): # проходим циклом по изображению пользователя
            for j in range(1, y - 1):
                r, g, b, alpha = pixels_im[i, j]
                r += 100
                g += 100
                b += 100
                if r > 255:
                    r = 255
                if g > 255:
                    g = 255
                if b > 255:
                    b = 255
                pixels_im[i, j] = r, g, b, alpha
                if pixels_qr[i, j] == 0:
                    pixels_im[i, j] = (0, 0, 0) # перерисовываем черные пиксели c qr на изображение пользователя
                else:
                    for p in range(-1, 2):
                        for t in range(-1, 2):
                            if pixels_qr[i + p, j + t] == 0:
                                pixels_im[i, j] = (255, 255, 255) # делаем окантовку вокруг черных пикселей qr
        im.save(f"qr/{self.qr_name + '.png'}") # сохраняем

    def qr_decode(self):
        im = cv.imread(self.qr_name + '.png') # читаем qr
        det = cv.QRCodeDetector()

        text, points, straight_qrcode = det.detectAndDecode(im) # получаем данные о qr с помощью машинного зрения
        return text # возращаем только текст

    def make_gif(self, name='gif', name_fon='fon'):
        gif_base = Image.open('immutable_files/image_base.png')
        gif_base = gif_base.resize((500, 500))
        fon = Image.open(f'pass/{name_fon}.png')
        fon = fon.resize((500, 500))
        pixels_gif = gif_base.load()
        pixels_fon = fon.load()

        for x in range(500):
            for y in range(500):
                if pixels_gif[x, y][1] == 255:
                    pixels_gif[x, y] = pixels_fon[x, y]

        frames = [gif_base] # список кадров

        gif_base.save(f'pass/{name}-2.png')

        for i in range(36):
            gif_base = Image.open(f'pass/{name}-2.png')

            gif_base = gif_base.rotate(-10) # вращаем изображение

            frames.append(gif_base) # добавляем изображения в список

            gif_base.save(f'pass/{name}-2.png')

        frames[0].save(
            f'gif/{name}.gif',
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            duration=50,
            loop=0
        ) # сохраняем с нужными параметрами (через параметр duration можно ускорить или замедлить гиф)
        os.remove(f'pass/{name}-2.png')

    def statistic_image(self, user_id, listen_count, add_count, ad_count):
        im = Image.open('immutable_files/statistic_back_image.png')
        im.resize((500, 500))

        fnt = ImageFont.truetype(f"immutable_files/font/10.12_4_cyr-lat.ttf", 40)

        d = ImageDraw.Draw(im)

        d.multiline_text((100, 100), 
        f"Ваша статистика\n\n\n\nСчёт прослушивания:{listen_count}\n\n\nСчёт добавления:{add_count}\n\n\nСчёт рекламы:{ad_count}", 
        font=fnt, fill=(255, 255, 255))

        im.save(f"pass/statistic-{user_id}.jpg")