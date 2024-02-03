# from PIL import Image
#
#
# def Image_parser_f(im, fragment_size):
#     im = Image.open(im)
#     pixels = im.load()  # список с пикселями
#     x, y = im.size  # ширина (x) и высота (y) изображения
#
#     for i in range(x // fragment_size[0]):
#         for j in range(y // fragment_size[1]):
#             im.crop(box=(x // fragment_size[0] * i, y // fragment_size[1] * j, x // fragment_size[0] * (i+1)-1,y // fragment_size[1] * (j+1)-1)).save('im_pars\image{0}{1}.png'.format(str(i+1), str(j+1)))
#
#
# Image_parser_f("танки.png", (16, 16)
import os
import time

from PIL import Image

def split_and_save_image(file_path, fragment_size, save_dir, mode):
    fragments = list()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with Image.open(file_path) as img:
        # определяем размеры исходного изображения
        width, height = img.size

        # определяем количество фрагментов по ширине и высоте
        rows = height // fragment_size[1]
        cols = width // fragment_size[0]

        # разрезаем изображение на фрагменты и сохраняем каждый фрагмент в папке
        for i in range(rows):
            for j in range(cols):
                x = j * fragment_size[0]
                y = i * fragment_size[1]
                fragment = img.crop((x, y, x + fragment_size[0], y + fragment_size[1]))
                if "save" in mode:
                    fragment.save(os.path.join(save_dir, f"fragment_{i}_{j}.png"), "PNG")
                if "ret" in mode:
                    if "fragments" not in locals():
                        fragments = list()
                    fragments.append(fragment.resize((16 * 3, 16 * 3), resample=Image.NEAREST))
        return fragments


# split_and_save_image('танкибезфона.png', (16, 16), 'fragments', "save")
# split_and_save_image('танкибезфона.png', (16, 16), 'fragments', "ret")
import pyautogui
run = True
while run:
    time.sleep(1.2)
    pyautogui.leftClick()