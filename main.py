import time

from import_libraries import *
import copy
import neat
import pygame
import random
import sys
import threading
import traceback

import pygame as pg

from test import astar


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Oбнаружена ошибка !:", tb)


#    QtWidgets.QApplication.quit()             # !!! если вы хотите, чтобы событие завершилось

sys.excepthook = excepthook
class Settings_game:
    def __init__(self):
        pg.init()
        # открываем txt файл с игровой картой
        g_c_str = open("Game_card.txt", "r")
        game_card = list()
        for i in g_c_str:
            game_card.append(i.rstrip())
        # ширина и высота изображения танка
        self.delta_tanks_spr = 48
        # определяем размеры окна (зависит от размера игровой карты на txt)
        self.screen_dimensions = (len(game_card[0]) * self.delta_tanks_spr, len(game_card) * self.delta_tanks_spr)
        # создаём окно pygame с параметром размера определённом раньше

        # записываем список с изображениями танка в разных состояниях для последуюшей анимации
        self.tanks = [pg.image.load("Tank_im\Icon_tank1_u.png"),  # езда вверх
                      pg.image.load("Tank_im\Icon_tank1_d.png"),  # езда вниз
                      pg.image.load("Tank_im\Icon_tank1_l.png"),  # езда влево
                      pg.image.load("Tank_im\Icon_tank1_r.png")]  # езда вправо
        # записываем список с изображениями пули в разных состояниях для последуюшей анимации
        self.bullets = [pg.image.load("Bullet_im\Im_bullet_u.png"),  # полёт вверх
                        pg.image.load("Bullet_im\Im_bullet_d.png"),  # полёт вниз
                        pg.image.load("Bullet_im\Im_bullet_l.png"),  # полёт влево
                        pg.image.load("Bullet_im\Im_bullet_r.png"),  # полёт вправо
                        pg.image.load("Bullet_im\Im_bullet_u_1.bmp")]  # взрыв
        # список со всеми звуками
        self.music_list = [pg.mixer.Sound(r"ogg\tanks_battle-city-sfx-6.ogg"),
                           pg.mixer.Sound(r"ogg\player.move.ogg")]
        # оздаём список в котором будут храниться все обьекты карты
        self.list_tanks_and_blocks = list()
        # self.window = pg.display.set_mode(self.screen_dimensions)
        self.bonus_list = list()
set_game = Settings_game()


class Buttons:
    def __init__(self, x_and_y, im, f, args="NOARGS", text="", blocking=False, f_if_in_focus=lambda: None):
        self.f_if_in_focus = f_if_in_focus
        self.blocking = blocking
        self.args = args

        self.hc = None
        self.x_and_y = x_and_y
        self.im: pg.Surface = im
        self.size_im = self.im.get_size()
        self.f = f
        self.activ = False
        self.font_for_text = pg.font.Font("fonts\ofont.ru_Acherus Feral__.ttf", 25)
        self.str_text = str(text)
        self.text = self.font_for_text.render(str(text), True, (190, 0, 0))

    def set_negative_fill(self, surface):
        w, h = surface.get_size()
        for x in range(w):
            for y in range(h):
                self.hc = surface.get_at((x, y))
                surface.set_at((x, y), pg.Color(255 - self.hc[0], 255 - self.hc[1], 255 - self.hc[2], self.hc[3]))
        if self.activ:
            self.activ = False
        else:
            self.activ = True
        self.draw(pg.display.get_surface())

    def click_or_not_click(self, event):
        pass

    def get_f(self):
        if self.args != "NOARGS":
            return self.f(self.args, parent=self)
        return self.f(parent=self)

    def f_if_focus(self):
        return self.f_if_in_focus()
    def draw(self, window):
        if pg.display.get_init():
            window.blit(self.im, self.x_and_y)
            window.blit(self.text, (self.x_and_y[0] + self.size_im[0] / 2 - self.font_for_text.size(self.str_text)[0] / 2, self.x_and_y[1] + self.size_im[1] / 2 - self.font_for_text.size(" ")[1] / 2))
class Fix_Buttons(Buttons):
    def click_or_not_click(self, event):
        if event == pg.MOUSEBUTTONDOWN:
            position = pg.mouse.get_pos()
            if position[0] in range(self.x_and_y[0], self.x_and_y[0] + self.size_im[0]) and position[1] in range(self.x_and_y[1], self.x_and_y[1] + self.size_im[1]):
                self.get_f()
                self.set_negative_fill(self.im)
                pg.mixer_music.load(r"ogg\zvuk41.mp3")
                pg.mixer_music.play()
                return True
            return False

class Push_Buttons(Buttons):
    def click_or_not_click(self, event):
        position = pg.mouse.get_pos()
        if position[0] in range(self.x_and_y[0], self.x_and_y[0] + self.size_im[0]) and position[1] in range(self.x_and_y[1], self.x_and_y[1] + self.size_im[1]):
            if event == pg.MOUSEBUTTONDOWN and not self.blocking:
                    self.get_f()
                    self.set_negative_fill(self.im)
                    pg.mixer_music.load(r"ogg\zvuk41.mp3")
                    pg.mixer_music.play()
                    return True
            elif event == pg.MOUSEBUTTONUP and self.activ and not self.blocking:
                self.set_negative_fill(self.im)
                pg.mixer_music.load(r"ogg\zvuk41.mp3")
                pg.mixer_music.play()
                return False
            elif event == pg.MOUSEWHEEL or pg.MOUSEMOTION:
                self.f_if_focus()
        if event == pg.MOUSEBUTTONUP and self.activ and not self.blocking:
            self.set_negative_fill(self.im)
            pg.mixer_music.play()


# класс пуль
class Bullets:
    # нициализация
    def __init__(self, poz, x_and_y, tank, im_b=set_game.bullets[0], speed=10, damage=1, up_h=22, down_h=23, left_h=23, right_h=22):
        self.x_and_y = x_and_y
        self.damage = damage
        self.bullet_aktiv = False
        self.im_b = im_b
        self.speed = speed
        self.poz = poz
        self.no_flight_completed = False
        self.list_tanks_and_blocks = set_game.list_tanks_and_blocks
        self.my_tank = tank
        self.up_h = up_h
        self.down_h = down_h
        self.left_h = left_h
        self.right_h = right_h

    # полёт вверх
    def up(self):
        # меняем координаты
        self.x_and_y = (self.x_and_y[0], self.x_and_y[1] - self.speed)
        # анимация
        self.im_b = set_game.bullets[0]
        # если не в полёте пулю телепортировать к танку
        if not self.no_flight_completed:
            set_game.music_list[0].play()
            self.x_and_y = (self.x_and_y[0] + self.up_h, self.x_and_y[1] - 2)
            self.no_flight_completed = True
        # проверка на столкновения
        for i in self.list_tanks_and_blocks:
            if self.x_and_y[0] in range(i.return_pozitional()[0], i.return_pozitional()[0] + set_game.delta_tanks_spr):
                if self.x_and_y[1] in range(i.return_pozitional()[1],
                                            i.return_pozitional()[1] + set_game.delta_tanks_spr):

                    # if i.return_pozitional()[0] in prange(self.x_and_y[0],
                    #                                      self.x_and_y[0] + set_game.delta_tanks_spr):
                    #     if i.return_pozitional()[1] \
                    #             in prange(self.x_and_y[1] - set_game.delta_tanks_spr, self.x_and_y[1]):
                    #         # столкновение с блоком
                    if isinstance(i, Blocks):
                        pg.mixer.Sound(r"ogg\brickErase.ogg").play()
                        set_game.music_list[0].stop()
                        return "block", i  # return collision_with_a
                    # столкновение с танком
                    if isinstance(i, Tanks):
                        return "tank", i  # return collision_with_a

    # далее в последующих 3 методах принцип будет таким-же поменяються толька направления

    # вниз
    def down(self):
        self.x_and_y = (self.x_and_y[0], self.x_and_y[1] + self.speed)
        self.im_b = set_game.bullets[1]
        if not self.no_flight_completed:
            set_game.music_list[0].play()
            self.x_and_y = (self.x_and_y[0] + self.down_h, self.x_and_y[1])
            self.no_flight_completed = True
        for i in self.list_tanks_and_blocks:
            if self.x_and_y[0] in range(i.return_pozitional()[0],
                                        i.return_pozitional()[0] + set_game.delta_tanks_spr):
                if self.x_and_y[1] \
                        in range(i.return_pozitional()[1], i.return_pozitional()[1] + set_game.delta_tanks_spr):
                    if isinstance(i, Blocks):
                        set_game.music_list[0].stop()
                        # pg.mixer.Sound(r"ogg\brickErase.ogg").play()
                        pg.mixer.Sound(r"ogg\brickErase.ogg").play()
                        set_game.music_list[0].stop()
                        return "block", i  # return collision_with_a
                    if isinstance(i, Tanks):
                        return "tank", i  # return collision_with_a

    # влево
    def left(self):
        self.x_and_y = (self.x_and_y[0] - self.speed, self.x_and_y[1])
        self.im_b = set_game.bullets[2]
        if not self.no_flight_completed:
            set_game.music_list[0].stop()
            self.x_and_y = (self.x_and_y[0], self.x_and_y[1] + self.left_h)
            self.no_flight_completed = True
        for i in self.list_tanks_and_blocks:
            if i.return_pozitional()[0] in range(self.x_and_y[0] - set_game.delta_tanks_spr,
                                                 self.x_and_y[0]):
                if i.return_pozitional()[1] \
                        in range(self.x_and_y[1] - set_game.delta_tanks_spr, self.x_and_y[1]):
                    if isinstance(i, Blocks):
                        pg.mixer.Sound(r"ogg\brickErase.ogg").play()
                        set_game.music_list[0].stop()
                        return "block", i  # return collision_with_a
                    if isinstance(i, Tanks):
                        return "tank", i  # return collision_with_a

    # вправо
    def right(self):
        self.x_and_y = (self.x_and_y[0] + self.speed, self.x_and_y[1])
        self.im_b = set_game.bullets[3]
        if not self.no_flight_completed:
            set_game.music_list[0].play()
            self.x_and_y = (self.x_and_y[0], self.x_and_y[1] + self.right_h)
            self.no_flight_completed = True
        for i in self.list_tanks_and_blocks:
            if i.return_pozitional()[0] in range(self.x_and_y[0] - set_game.delta_tanks_spr,
                                                 self.x_and_y[0]):
                if i.return_pozitional()[1] \
                        in range(self.x_and_y[1] - set_game.delta_tanks_spr, self.x_and_y[1]):
                    if isinstance(i, Blocks):
                        pg.mixer.Sound(r"ogg\brickErase.ogg").play()
                        set_game.music_list[0].stop()
                        return "block", i  # return collision_with_a
                    if isinstance(i, Tanks):
                        return "tank", i  # return collision_with_a

    # отрисовка
    def draw(self, window):
        window.blit(self.im_b, self.x_and_y)

    # возвращяет координаты в формате (x, y)
    def return_pozitional(self):
        return self.x_and_y

    # метод для выстрела
    def fire(self):

        if self.poz == self.my_tank.ims_tank[0]:
            return self.up()
        elif self.poz == self.my_tank.ims_tank[1]:
            return self.down()
        elif self.poz == self.my_tank.ims_tank[2]:
            return self.left()
        else:
            return self.right()


# класс танков
class Tanks:
    def __init__(self, x_and_y, im=set_game.tanks[3], speed=5, health=5, damade=1, ims_tank=set_game.tanks):
        self.run_lvl = True
        self.x_and_y = x_and_y
        self.im_t = im
        self.speed = speed
        self.health = health
        self.bullet_aktiv = False
        self.bullet = 0
        self.damade = damade
        self.ims_tank = ims_tank
        self.BUMEVENTTYPE = pygame.USEREVENT + 20
        self.go_to = (None, lambda: None)
        pygame.time.set_timer(self.BUMEVENTTYPE, 20)
        self.bum_event_timer = 0

        self.expl = Explosion(self, self.x_and_y, pg.display.get_surface())
    # ф-ю для опроса сети стороны движения

    def init_move(self, fl_fire=pg.key.get_pressed()[pg.K_SPACE],
                  fl_right=pg.key.get_pressed()[pg.K_RIGHT],
                  fl_lelf=pg.key.get_pressed()[pg.K_LEFT],
                  fl_down=pg.key.get_pressed()[pg.K_DOWN],
                  fl_up=pg.key.get_pressed()[pg.K_UP]):
        if isinstance(self.bullet, Bullets):
            self.T = True
        else:
            self.T = False
        if fl_fire or self.T:
            self.T = self.fire()
        if fl_right and isinstance(self, Tanks):
            self.right()
        elif fl_lelf and isinstance(self, Tanks):
            self.left()
        elif fl_down and isinstance(self, Tanks):
            self.down()
        elif fl_up and isinstance(self, Tanks):
            self.up()


    # проверка, иничтожен ли танк
    def is_live(self):
        if self.health <= 0:
            pass
            pg.mixer.Sound(r"ogg/buh.ogg").play()

        return not self.health <= 0

    # метод для проверки куда можно ходить,
    # возвращяет список в формате [0 or 1, 0 or 1, 0 or 1, 0 or 1]
    #                                up     down    left    right
    # 0 - go    1-stop

    def return_side_go(self):
        side = []

        # условие для верха
        for i in self.list_tanks_and_blocks:
            if i.return_pozitional()[0] in range(self.x_and_y[0] - set_game.delta_tanks_spr + 10,
                                                 self.x_and_y[0] + set_game.delta_tanks_spr - 10):
                if i.return_pozitional()[1] \
                        in range(self.x_and_y[1] - set_game.delta_tanks_spr, self.x_and_y[1]):
                    side.append(1)
                    break
            elif self.return_pozitional()[1] < 0:
                side.append(1)
                break
        else:
            side.append(0)
        # условие для низа

        for i in self.list_tanks_and_blocks:
            if i.return_pozitional()[0] in range(self.x_and_y[0] - set_game.delta_tanks_spr + 10,
                                                 self.x_and_y[0] + set_game.delta_tanks_spr - 10):
                if i.return_pozitional()[1] - set_game.delta_tanks_spr \
                        in range(self.x_and_y[1] - set_game.delta_tanks_spr, self.x_and_y[1]):
                    side.append(1)
                    break
            elif self.return_pozitional()[1] > set_game.screen_dimensions[1] - set_game.delta_tanks_spr:
                side.append(1)
                break
        else:
            side.append(0)
        # условие для лева

        for i in self.list_tanks_and_blocks:
            if self.return_pozitional()[1] \
                    in range(i.return_pozitional()[1] - set_game.delta_tanks_spr + 10,
                             i.return_pozitional()[1] + set_game.delta_tanks_spr - 10):
                if self.return_pozitional()[0] \
                        in range(i.return_pozitional()[0], i.return_pozitional()[0] + set_game.delta_tanks_spr):
                    side.append(1)
                    break
            elif self.return_pozitional()[0] < 0:
                side.append(0)
                break
        else:
            side.append(0)
        # условие для право

        for i in self.list_tanks_and_blocks:
            if self.return_pozitional()[1] \
                    in range(i.return_pozitional()[1] - set_game.delta_tanks_spr + 10,
                             i.return_pozitional()[1] + set_game.delta_tanks_spr - 10):
                if self.return_pozitional()[0] + set_game.delta_tanks_spr \
                        in range(i.return_pozitional()[0], i.return_pozitional()[0] + set_game.delta_tanks_spr):
                    side.append(1)
                    break
            elif self.return_pozitional()[0] > set_game.screen_dimensions[0] - set_game.delta_tanks_spr:
                side.append(1)
                break
        else:
            side.append(0)
        return side

    def return_vert(self):
        side = []

        # условие для верха
        for i in self.list_tanks_and_blocks:
            # if i.return_pozitional()[0] in prange(0 - delta_tanks_spr + 10,
            #                                          screen_dimensions[0] + delta_tanks_spr - 10):
            z = i.begehbar
            g = range(self.x_and_y[1], self.x_and_y[1] + set_game.delta_tanks_spr)

            if i.return_pozitional()[1] \
                    in range(self.x_and_y[1], self.x_and_y[1] + set_game.delta_tanks_spr):
                if i.begehbar:
                    side.append(0)
                else:
                    side.append(1)
        return side

    # метод для добавления в список всех обьектов
    def init_fisic(self, mode="kl"):
        if self.is_live():
            if self not in set_game.list_tanks_and_blocks and mode == "kl":
                set_game.list_tanks_and_blocks.append(self)
            self.list_tanks_and_blocks = copy.copy(set_game.list_tanks_and_blocks)
            if self in self.list_tanks_and_blocks:
                self.list_tanks_and_blocks.remove(self)
        if not self.is_live() and self in set_game.list_tanks_and_blocks:
            set_game.list_tanks_and_blocks.remove(self)

    # возврат координат в формате (x, y)
    def return_pozitional(self):
        return self.x_and_y

    # направление
    # 0-up, 1-down, 2-left, 3-right
    def direction(self):
        if self.im_t == self.ims_tank[0]:
            return 0
        elif self.im_t == self.ims_tank[1]:
            return 1
        elif self.im_t == self.ims_tank[2]:
            return 2
        else:
            return 3

    def up(self):
        # анимация
        self.im_t = self.ims_tank[0]
        # проверка можно ли проехать
        for i in self.list_tanks_and_blocks:
            if i.return_pozitional()[0] in range(self.x_and_y[0] - set_game.delta_tanks_spr + 10,
                                                 self.x_and_y[0] + set_game.delta_tanks_spr - 10):
                if i.return_pozitional()[1] \
                        in range(self.x_and_y[1] - set_game.delta_tanks_spr, self.x_and_y[1]):
                    return 'stop'
        if self.return_pozitional()[1] > 0:
            # смена координат
            self.x_and_y = (self.x_and_y[0], self.x_and_y[1] - self.speed)
        return 'go'

    def down(self):
        self.im_t = self.ims_tank[1]
        for i in self.list_tanks_and_blocks:
            if i.return_pozitional()[0] in range(self.x_and_y[0] - set_game.delta_tanks_spr + 10,
                                                 self.x_and_y[0] + set_game.delta_tanks_spr - 10):
                if i.return_pozitional()[1] - set_game.delta_tanks_spr \
                        in range(self.x_and_y[1] - set_game.delta_tanks_spr, self.x_and_y[1]):
                    return 'stop'
        if self.return_pozitional()[1] < set_game.screen_dimensions[1] - set_game.delta_tanks_spr:
            self.x_and_y = (self.x_and_y[0], self.x_and_y[1] + self.speed)
        return 'go'

    def left(self):
        self.im_t = self.ims_tank[2]
        for i in self.list_tanks_and_blocks:
            if self.return_pozitional()[1] \
                    in range(i.return_pozitional()[1] - set_game.delta_tanks_spr + 10,
                             i.return_pozitional()[1] + set_game.delta_tanks_spr - 10):
                if self.return_pozitional()[0] \
                        in range(i.return_pozitional()[0], i.return_pozitional()[0] + set_game.delta_tanks_spr):
                    return 'stop'
        if self.return_pozitional()[0] > 0:
            self.x_and_y = (self.x_and_y[0] - self.speed, self.x_and_y[1])
        return 'go'

    def right(self):
        for i in self.list_tanks_and_blocks:
            if self.return_pozitional()[1] \
                    in range(i.return_pozitional()[1] - set_game.delta_tanks_spr + 10,
                             i.return_pozitional()[1] + set_game.delta_tanks_spr - 10):
                if self.return_pozitional()[0] + set_game.delta_tanks_spr \
                        in range(i.return_pozitional()[0], i.return_pozitional()[0] + set_game.delta_tanks_spr):
                    return 'stop'
        if self.return_pozitional()[0] < set_game.screen_dimensions[0] - set_game.delta_tanks_spr:
            self.x_and_y = (self.x_and_y[0] + self.speed, self.x_and_y[1])
        self.im_t = self.ims_tank[3]
        return 'go'

    def fire_will_successful(self):
        if self.direction() == 0:
            sizes = list()
            for i in self.list_tanks_and_blocks:
                if self.x_and_y[0] in range(i.return_pozitional()[0],
                                            i.return_pozitional()[0] + set_game.delta_tanks_spr) and self.x_and_y[1] > \
                        i.x_and_y[1]:
                    if isinstance(i, Blocks):
                        sizes.append(i.x_and_y[1])
                    if i == self.enemy:
                        if isinstance(i, Tanks) and max(sizes) < i.x_and_y[1]:
                            return 1
        return 0

    def size_to_wall(self):
        self.sizes_to_wall = list((1000000000000, 100000000000000000))
        if self.direction() == 0:
            for i in self.list_tanks_and_blocks:
                if self.return_pozitional()[0] + 22 in \
                        range(i.return_pozitional()[0], i.return_pozitional()[0] + set_game.delta_tanks_spr):
                    # if not "self.sizes_to_wall" in locals():
                    # self.sizes_to_wall = list()
                    if not self.return_pozitional()[1] - i.return_pozitional()[1] < 0 and not isinstance(i, Tanks):
                        self.sizes_to_wall.append(abs(self.return_pozitional()[1] - i.return_pozitional()[1]))
            self.sizes_to_wall = min(*self.sizes_to_wall, 1000)
        elif self.direction() == 1:
            for i in self.list_tanks_and_blocks:
                if self.return_pozitional()[0] + 22 in \
                        range(i.return_pozitional()[0], i.return_pozitional()[0] + set_game.delta_tanks_spr):
                    # if not "self.sizes_to_wall" in locals():
                    # self.sizes_to_wall = list()
                    if not self.return_pozitional()[1] - i.return_pozitional()[1] > 0 and not isinstance(i, Tanks):
                        self.sizes_to_wall.append(abs(self.return_pozitional()[1] - i.return_pozitional()[1]))
            self.sizes_to_wall = min(*self.sizes_to_wall, 1000)
        elif self.direction() == 2:
            for i in self.list_tanks_and_blocks:
                if self.return_pozitional()[1] + 23 in \
                        range(i.return_pozitional()[1], i.return_pozitional()[1] + set_game.delta_tanks_spr):
                    # if not "self.sizes_to_wall" in locals():
                    # self.sizes_to_wall = list()
                    if not self.return_pozitional()[0] - i.return_pozitional()[0] < 0 and not isinstance(i, Tanks):
                        self.sizes_to_wall.append(abs(self.return_pozitional()[0] - i.return_pozitional()[0]))
            self.sizes_to_wall = min((*self.sizes_to_wall, 1000))
        elif self.direction() == 3:
            for i in self.list_tanks_and_blocks:
                if self.return_pozitional()[1] + 23 in \
                        range(i.return_pozitional()[1], i.return_pozitional()[1] + set_game.delta_tanks_spr):
                    # if not "self.sizes_to_wall" in locals():
                    # self.sizes_to_wall = list()
                    if not self.return_pozitional()[0] - i.return_pozitional()[0] > 0 and not isinstance(i, Tanks):
                        self.sizes_to_wall.append(abs(self.return_pozitional()[0] - i.return_pozitional()[0]))
            self.sizes_to_wall = min((*self.sizes_to_wall, 1000))
        return self.sizes_to_wall

    # выстрел
    def fire(self, up_h=22, down_h=23, left_h=23, right_h=22):
        if self.is_live():
            if isinstance(self.bullet, int):
                self.bullet = Bullets(self.im_t, (self.x_and_y[0], self.x_and_y[1]), self, damage=self.damade, up_h=up_h, down_h=down_h, left_h=left_h, right_h=right_h)
            collision = self.bullet.fire()
            if collision == None:
                collision = "no"

            if any((self.bullet.return_pozitional()[0] > set_game.screen_dimensions[0],
                    self.bullet.return_pozitional()[1] > set_game.screen_dimensions[1],
                    self.bullet.return_pozitional()[0] < 0,
                    self.bullet.return_pozitional()[1] < 0)) or collision[0] == "block":
                del self.bullet
                self.bullet = 0
                return False
            elif collision[0] == "tank" and not collision[1] == self and "enemy" not in dir(self):
                collision[1].health -= self.bullet.damage
                del self.bullet
                self.bullet = 0
                return False
            elif collision[0] == "tank" and not collision[1] == self and "enemy" in dir(self) and self.enemy == collision[1]:
                collision[1].health -= self.bullet.damage
                del self.bullet
                self.bullet = 0
                return False
            return True

    # отрисовка
    def draw(self, window, sise_x=1):
        if self.is_live():
            if isinstance(self.bullet, Bullets):
                self.bullet.draw(window)
            im_t = pygame.transform.scale(self.im_t, (self.im_t.get_width() * sise_x, self.im_t.get_width() * sise_x))
            window.blit(im_t, self.x_and_y)
            self.list_tanks = copy.copy(set_game.list_tanks_and_blocks)
            if self in self.list_tanks:
                self.list_tanks.remove(self)
        else:
            if self in set_game.list_tanks_and_blocks:
                set_game.list_tanks_and_blocks.remove(self)
            self.expl.start(self.x_and_y)
            self.is_live = lambda: False
            self.init_move = lambda p, fl_right=pg.key.get_pressed()[pg.K_RIGHT], fl_lelf=pg.key.get_pressed()[pg.K_LEFT], fl_down=pg.key.get_pressed()[pg.K_DOWN], fl_up=pg.key.get_pressed()[pg.K_UP]: None

    def get_data(self, mode="kl"):
        if mode == "kl":
            bullet_can_use = 0
            if isinstance(self.bullet, Bullets):
                bullet_can_use = 1
            return *[i / (set_game.delta_tanks_spr * 16) for i in self.x_and_y], *[i / (set_game.delta_tanks_spr * 16)
                                                                                   for i in self.enemy.x_and_y]
        else:
            return random.randint(0, 768) / (set_game.delta_tanks_spr * 16), random.randint(0, 768) / (
                    set_game.delta_tanks_spr * 16), random.randint(0, 768) / (
                           set_game.delta_tanks_spr * 16), random.randint(0, 768) / (set_game.delta_tanks_spr * 16)

    def update_direction(self):
        if hasattr(self, "TOP_NEIRO_GENOM"):
            self.winner_net = neat.nn.FeedForwardNetwork.create(self.TOP_NEIRO_GENOM, self.config)
            print(self.TOP_NEIRO_GENOM)
            get_data = self.get_data(mode="kl")
            output = self.winner_net.activate(get_data)
            max_output = output.index(max(output))
            error = 0

            if get_data[1] > get_data[3] and max_output != 0:
                error += 2.0
            elif get_data[1] > get_data[3] and max_output == 0:
                error -= 2.0
            if get_data[1] < get_data[3] and max_output != 1:
                error += 2.0
            elif get_data[1] < get_data[3] and max_output == 1:
                error -= 2.0
            if get_data[0] > get_data[2] and max_output != 2:
                error += 2.0
            elif get_data[0] > get_data[2] and max_output == 2:
                error -= 2.0
            if get_data[0] < get_data[2] and max_output != 3:
                error += 2.0
            elif get_data[0] < get_data[2] and max_output == 3:
                error -= 2.0
            if max_output == 0:
                self.go_to = (0, self.up)
            if max_output == 1:
                self.go_to = (1, self.down)
            if max_output == 2:
                self.go_to = (2, self.left)
            if max_output == 3:
                self.go_to = (3, self.right)
            if (self.go_to[0] == 2 or self.go_to[0] == 3) and abs(
                    self.x_and_y[0] - self.enemy.x_and_y[0]) < self.speed and self.x_and_y[0] != self.enemy.x_and_y[0]:
                self.x_and_y = (self.enemy.x_and_y[0], self.x_and_y[1])
            elif (self.go_to[0] == 0 or self.go_to[0] == 1) and abs(
                    self.x_and_y[1] - self.enemy.x_and_y[1]) < self.speed and self.x_and_y[1] != self.enemy.x_and_y[1]:
                self.x_and_y = (self.x_and_y[0], self.enemy.x_and_y[1])
            else:
                self.go_to[1]()
            self.TOP_NEIRO_GENOM.fitness = error

    def eval_genome(self, genomes, config):
        self.nets = []

        for i, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            self.nets.append(net)
            error = 0
            get_data = self.get_data(mode="random")

            output = net.activate(get_data)
            max_output = output.index(max(output))
            self.enemy: Tanks
            side_go = self.return_side_go()
            if get_data[1] > get_data[3] and max_output != 0:
                error += 4.0
            elif get_data[1] > get_data[3] and max_output == 0:
                error -= 2.0
            if get_data[1] < get_data[3] and max_output != 1:
                error += 4.0
            elif get_data[1] < get_data[3] and max_output == 1:
                error -= 2.0
            if get_data[0] > get_data[2] and max_output != 2:
                error += 4.0
            elif get_data[0] > get_data[2] and max_output == 2:
                error -= 2.0
            if get_data[0] < get_data[2] and max_output != 3:
                error += 4.0
            elif get_data[0] < get_data[2] and max_output == 3:
                error -= 2.0

            # if abs(self.enemy.x_and_y[0] - self.x_and_y[0]) < set_game.delta_tanks_spr and (self.direction() == 0 or self.direction() == 1) and isinstance(self.bullet, Bullets) and self.fire_will_successful() == 1:
            #     self
            g.fitness = 0 - error + abs(self.x_and_y[0] - self.enemy.x_and_y[0])

    # def evolve_2(self):
    #     for generation in range(5):
    #         self.population.run(eval(), 1)  # Оценка геномов на одну итерацию

    def evolve(self):
        print("eval is stated")
        self.config_path = 'neiro_config.txt'
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                  neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                  self.config_path)

        self.population = neat.Population(self.config)
        self.NEIRO_NETWORK_POPULATION = self.population.run(self.eval_genome, 15)
        self.TOP_NEIRO_GENOM = self.population.best_genome

    def return_pozition_in_pix(self):
        k1 = tuple([(i) // 48 for i in self.x_and_y])
        if "x_and_y_in_pix" not in dir(self):
            self.x_and_y_in_pix = copy.copy(list(k1))
        k2 = tuple([(i + 48) // 48 for i in self.x_and_y])
        print(k1[0] * 48, k2[0] * 48)
        if self.x_and_y[0] in range(k1[0] * 48 - 5, k2[0] * 48 + 5) and self.x_and_y[0] + 48 in range(k1[0] * 48 - 5, k2[0] * 48 + 5):
            self.x_and_y_in_pix[0] = k1[0]
        if self.x_and_y[1] in range(k1[1] * 48 - 5, k2[1] * 48 + 5) and self.x_and_y[1] + 48 in range(k1[1] * 48 - 5, k2[1] * 48 + 5):
            self.x_and_y_in_pix[1] = k1[1]
        return self.x_and_y_in_pix

    def go_to_enemy(self):
        while self.run_lvl:
            start_point, end_point = self.return_pozition_in_pix(), self.enemy.return_pozition_in_pix()
            try:
                print(start_point, end_point, set_game.hardness_map)

                path = astar(set_game.hardness_map, start_point, end_point)
                print("Путь найден:", path)
                self.path = path[1][::-1]
                poz_in_pix = self.return_pozition_in_pix()
                if self.path[1] < poz_in_pix[1]:
                    self.up()
                if self.path[1] > poz_in_pix[1]:
                    self.down()
                if self.path[0] < poz_in_pix[0]:
                    self.left()
                if self.path[0] > poz_in_pix[0]:
                    self.right()
                time.sleep(0.1)
                if self.enemy.return_pozition_in_pix()[1] == self.return_pozition_in_pix()[1] and self.enemy.return_pozition_in_pix()[0] > self.return_pozition_in_pix()[0] and self.direction() == 3:
                    self.fire()
                if self.enemy.return_pozition_in_pix()[1] == self.return_pozition_in_pix()[1] and self.enemy.return_pozition_in_pix()[0] < self.return_pozition_in_pix()[0] and self.direction() == 2:
                    self.fire()
                if self.enemy.return_pozition_in_pix()[0] == self.return_pozition_in_pix()[0] and self.enemy.return_pozition_in_pix()[1] > self.return_pozition_in_pix()[1] and self.direction() == 1:
                    self.fire()
                if self.enemy.return_pozition_in_pix()[0] == self.return_pozition_in_pix()[0] and self.enemy.return_pozition_in_pix()[1] < self.return_pozition_in_pix()[1] and self.direction() == 0:
                    self.fire()
            except Exception as e:
                print(e)
                continue

    def start_ev(self):
        go_to_en_th = threading.Thread(target=self.go_to_enemy)
        go_to_en_th.start()
        return
        # # # Запускаем эволюцию в отдельном потоке
        # evolution_thread = threading.Thread(target=self.evolve)
        # evolution_thread.start()

class Bonus:
    def __init__(self, x_and_y, img):
        self.img = img
        self.x_and_y = x_and_y
    def drow(self, window: pg.Surface):
        if self.img != None:
            window.blit(self.img, self.x_and_y)

    def effect(self, object: Tanks):
        pass

    def give_effect(self):
        if self.img != None:
            for i in set_game.list_tanks_and_blocks:
                if self.x_and_y[0] in range(i.x_and_y[0] - set_game.delta_tanks_spr, i.x_and_y[0] + set_game.delta_tanks_spr):
                    if self.x_and_y[1] in range(i.x_and_y[1] - set_game.delta_tanks_spr,
                                                i.x_and_y[1] + set_game.delta_tanks_spr):
                        if isinstance(i, Blocks):
                            i: Blocks
                            if not i.begehbar:
                                self.drow = lambda s: None
                                self.give_effect = lambda : None
                        # столкновение с танком
                        if isinstance(i, Tanks):
                            self.img = None
                            self.effect(i)

class Invulnerability_Bonus(Bonus):
    def __init__(self, x_and_y):
        super().__init__(x_and_y, img=pg.transform.scale(pg.image.load(r"fragments\fragment_7_16.png"), [set_game.delta_tanks_spr] * 2))
        self.eff_start = False
        self.time = 8000000

    def drow(self, window: pg.Surface):
        if self.img != None:
            window.blit(self.img, self.x_and_y)
        if self.eff_start:
            self.invulnerability()
            print("invulnerability")

    def effect(self, object: Tanks):
        self.h = object.health
        self.tank = object
        self.eff_start = True


    def invulnerability(self):
            self.tank.is_live = lambda : True
            self.tank.health = self.h
class Explosion:
    def __init__(self, parent, x_and_y, window: pg.Surface):
        self.window = window
        self.parent = parent
        self.imgs = [pg.transform.scale(i, [set_game.delta_tanks_spr] * 2) for i in [pg.image.load(r"fragments\fragment_8_16.png"), pg.image.load(r"fragments\fragment_8_17.png"),
                pg.image.load(r"fragments\fragment_8_18.png")]]
        self.i = 0
        del self.parent
    def run(self):
        self.window.blit(self.imgs[self.i], self.x_and_y)
        pg.time.delay(30)

    def start(self, x_and_y):
        self.x_and_y = x_and_y
        if self.i == 3:
            return
        threading.Thread(target=self.run).run()
        self.i += 1
class Kettlebell_Tanks(Tanks):
    def __init__(self, x_and_y, type_t="p"):
        self.name = "Гиря"
        # p - player, e - enemy,
        if type_t == "p":
            imgs = [pg.image.load(r"fragments\fragment_7_0.png"), pg.image.load(r"fragments\fragment_7_4.png"),
                    pg.image.load(r"fragments\fragment_7_2.png"), pg.image.load(r"fragments\fragment_7_6.png"),]
        elif type_t == "e":
            imgs = [pg.image.load(r"fragments\fragment_7_8.png"), pg.image.load(r"fragments\fragment_7_12.png"),
                    pg.image.load(r"fragments\fragment_7_10.png"), pg.image.load(r"fragments\fragment_7_14.png"), ]
        imgs = [pg.transform.scale(i, (48, 48)) for i in imgs]
        super().__init__(x_and_y, imgs[3], 3, 40, 15, imgs)
    
    def fire(self):
        super().fire(21, 21, 21, 21)


class Compromise_Tanks(Tanks):
    def __init__(self, x_and_y, type_t="p"):
        self.name = "Компромисс"
        if type_t == "p":
            imgs = [pg.image.load(r"fragments\fragment_3_0.png"), pg.image.load(r"fragments\fragment_3_4.png"),
                    pg.image.load(r"fragments\fragment_3_2.png"), pg.image.load(r"fragments\fragment_3_6.png"), ]
        elif type_t == "e":
            imgs = [pg.image.load(r"fragments\fragment_3_8.png"), pg.image.load(r"fragments\fragment_3_12.png"),
                    pg.image.load(r"fragments\fragment_3_10.png"), pg.image.load(r"fragments\fragment_3_14.png"), ]
        imgs = [pg.transform.scale(i, (48, 48)) for i in imgs]
        super().__init__(x_and_y, imgs[3], 4, 30, 10, imgs)

    def fire(self):
        super().fire(23, 23, 22, 22)


class Nimble_APC(Tanks):
    def __init__(self, x_and_y, type_t="p"):
        self.name = """БТР "Шустрый" """
        if type_t == "p":
            imgs = [pg.image.load(r"fragments\fragment_5_0.png"), pg.image.load(r"fragments\fragment_5_4.png"),
                    pg.image.load(r"fragments\fragment_5_2.png"), pg.image.load(r"fragments\fragment_5_6.png"), ]
        elif type_t == "e":
            imgs = [pg.image.load(r"fragments\fragment_5_8.png"), pg.image.load(r"fragments\fragment_5_12.png"),
                    pg.image.load(r"fragments\fragment_5_10.png"), pg.image.load(r"fragments\fragment_5_14.png"), ]
        imgs = [pg.transform.scale(i, (48, 48)) for i in imgs]
        super().__init__(x_and_y, imgs[3], 6, 20, 5, imgs)

    def fire(self):
        super().fire(21, 21, 24, 21)

class Gnat_Tanks(Tanks):
    def __init__(self, x_and_y, type_t="p"):
        self.name = "Комарик"
        if type_t == "p":
            imgs = [pg.image.load(r"fragments\fragment_0_0.png"), pg.image.load(r"fragments\fragment_0_4.png"),
                    pg.image.load(r"fragments\fragment_0_2.png"), pg.image.load(r"fragments\fragment_0_6.png"), ]
        elif type_t == "e":
            imgs = [pg.image.load(r"fragments\fragment_0_8.png"), pg.image.load(r"fragments\fragment_0_12.png"),
                    pg.image.load(r"fragments\fragment_0_10.png"), pg.image.load(r"fragments\fragment_0_14.png"), ]
        imgs = [pg.transform.scale(i, (48, 48)) for i in imgs]
        super().__init__(x_and_y, imgs[3], 3, 10, 2, imgs)

    def fire(self):
        super().fire(22, 23, 23, 22)

class Die_Hard_Tanks(Tanks):
    def __init__(self, x_and_y, type_t="p"):
        self.name = "Крепкий Орешек "
        if type_t == "p":
            imgs = [pg.image.load(r"fragments\fragment_2_0.png"), pg.image.load(r"fragments\fragment_2_4.png"),
                    pg.image.load(r"fragments\fragment_2_2.png"), pg.image.load(r"fragments\fragment_2_6.png"), ]
        elif type_t == "e":
            imgs = [pg.image.load(r"fragments\fragment_2_8.png"), pg.image.load(r"fragments\fragment_2_12.png"),
                    pg.image.load(r"fragments\fragment_2_10.png"), pg.image.load(r"fragments\fragment_2_14.png"), ]

        imgs = [pg.transform.scale(i, (48, 48)) for i in imgs]
        super().__init__(x_and_y, imgs[3], 4, 25, 8, imgs)

    def fire(self):
        super().fire(21, 21, 21, 21)


# класс блоков
class Blocks:
    def __init__(self, type_block, x_and_y, begehbar):
        self.im = type_block
        self.x_and_y = x_and_y
        self.begehbar = begehbar
        set_game.list_tanks_and_blocks.append(copy.copy(self))

    # отрисовка
    def drow(self, window):
        window.blit(self.im, self.x_and_y)

    # возврат координат
    def return_pozitional(self):
        if self.begehbar:
            return (set_game.screen_dimensions[0] + 10, set_game.screen_dimensions[1] + 10)
        return self.x_and_y
