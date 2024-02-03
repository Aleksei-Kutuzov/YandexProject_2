# импортируем нужные библиотеки
import time

from import_libraries import *

from main import Bullets, Tanks, Blocks, Buttons, Push_Buttons, Fix_Buttons, Kettlebell_Tanks, Compromise_Tanks, \
    Nimble_APC, Gnat_Tanks, Die_Hard_Tanks, set_game, Invulnerability_Bonus, Settings_game


class Game_Tanks:
    def __init__(self, ):
        self.Tk_root = Tk()

        def excepthook(exc_type, exc_value, exc_tb):
            tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            print("Oбнаружена ошибка !:", tb)

        def next_tank(in_right, parent):
            if in_right and self.tank_index < len(self.tanks_list) - 1:
                self.tank_index += 1
            elif in_right and self.tank_index == len(self.tanks_list) - 1:
                self.tank_index = 0
            elif not in_right and self.tank_index != 0:
                self.tank_index -= 1
            elif not in_right and self.tank_index == 0:
                self.tank_index = len(self.tanks_list) - 1

        self.WINDOW_SETTINGS_SISE = 820, 550
        self.MAX_LEVELS = 25
        sys.excepthook = excepthook
        self.tank_index = 0
        self.tanks_list = [Gnat_Tanks, Nimble_APC, Die_Hard_Tanks, Compromise_Tanks, Kettlebell_Tanks]

        self.in_left_button = Push_Buttons(
            ((self.WINDOW_SETTINGS_SISE[0] // 2) - (150 // 2) - pg.image.load(r"buttons_im\LEFT.png").get_width(), 60),
            pg.image.load(r"buttons_im\LEFT.png"), next_tank, args=(False))
        self.in_right_button = Push_Buttons(((self.WINDOW_SETTINGS_SISE[0] // 2) + 150 // 2, 60),
                                            pg.image.load(r"buttons_im\RIGHT.png"), next_tank, args=(True))
        settings_window = pg.display.set_mode(self.WINDOW_SETTINGS_SISE)
        self.run_s = True
        self.levels_buttons = list()
        self.about_font = pg.font.Font("fonts/ocra(RUS BY LYAJKA).ttf", 20)
        self.status_fond = pg.font.Font("fonts/ofont.ru_Acherus Feral__.ttf", 18)
        self.tank_im = self.tanks_list[self.tank_index]((375, 50))
        lvl_num = 0
        con = sql.connect('for_game.db')
        with con:
            cur = con.cursor()
            cur.execute("SELECT name FROM player")
            self.user_name = cur.fetchall()[0][0]
            cur.execute("SELECT im_path FROM player")
            self.user_im_pash = cur.fetchall()[0][0]
            cur.execute("SELECT coins FROM player")
            self.user_coins = cur.fetchall()[0][0]
            cur.execute("SELECT maximum_level_passed FROM player")
            self.user_max_lvl = cur.fetchall()[0][0]
            cur.execute("SELECT skill FROM player")
            self.user_skill = cur.fetchall()[0][0]
            cur.execute("SELECT tanks FROM player")
            self.user_tanks = cur.fetchall()[0][0]
            print(self.user_tanks)
        con.close()
        self.user_im = pg.transform.scale(pg.image.load(self.user_im_pash), (65, 65))
        self.user_im_bitton = Push_Buttons((35, 45), self.user_im, self.open_file_dialog)
        self.user_name_lab = self.status_fond.render(self.user_name, True, (180, 0, 0))

        # def open_info_about_lvl(lvl_num):
        #     # con = sql.connect('for_game.db')
        #     # with con:
        #     #     cur = con.cursor()
        #     #     cur.execute("SELECT  FROM lvls")
        #     #     self.user_name = cur.fetchall()[0][0]
        #     #     cur.execute("SELECT im_path FROM player")
        #     #     self.user_im_pash = cur.fetchall()[0][0]
        #     #     cur.execute("SELECT coins FROM player")
        #     #     self.user_coins = cur.fetchall()[0][0]
        #     #     cur.execute("SELECT maximum_level_passed FROM player")
        #     #     self.user_max_lvl = cur.fetchall()[0][0]
        #     #     cur.execute("SELECT skill FROM player")
        #     #     self.user_skill = cur.fetchall()[0][0]
        #     # con.close()

        for i in range(3):
            for _i in range(9):
                lvl_num += 1
                if not self.user_max_lvl + 1 < lvl_num:
                    self.levels_buttons.append(Push_Buttons((_i * 90 + 10, i * 65 + 300), pg.transform.scale(
                        pg.image.load(r"Buttons_im\LEVEL_BUTTON.png"), (80, 60)), self.start_game, text=str(lvl_num),
                                                            args=(lvl_num), blocking=bool(self.user_max_lvl + 1 < lvl_num)))
                else:
                    self.levels_buttons.append(Push_Buttons((_i * 90 + 10, i * 65 + 300), pg.transform.scale(
                        pg.image.load(r"Buttons_im\BLOCKED_LEVEL_BUTTON.png"), (80, 60)), self.start_game, text=str(lvl_num),
                                                            args=(lvl_num), blocking=bool(self.user_max_lvl + 1 < lvl_num)))

        while self.run_s:
            self.about_tank = [self.about_font.render(f'{self.tank_im.name}', True,
                                                      (180, 0, 0)),
                               self.about_font.render(f'УРОН: {self.tank_im.damade}', True,
                                                      (180, 0, 0)),
                               self.about_font.render(f'ЗДОРОВЬЕ: {self.tank_im.health}', True,
                                                      (180, 0, 0)),
                               self.about_font.render(f'СКОРОСТЬ: {self.tank_im.speed}', True,
                                                      (180, 0, 0))]
            settings_window.fill((0, 0, 0))
            for i, _i in enumerate(self.about_tank):
                settings_window.blit(_i, (350, 20 * i + 150))
            pg.draw.rect(settings_window, (255, 127, 39), pg.Rect((self.WINDOW_SETTINGS_SISE[0] // 2) - (130 // 2), 35,
                                                                  (self.WINDOW_SETTINGS_SISE[0] // 2) - 140 * 2, 95), 4,
                         15)
            pg.draw.rect(settings_window, (255, 127, 39), pg.Rect((self.WINDOW_SETTINGS_SISE[0] // 2) - 180, 15,
                                                                  (self.WINDOW_SETTINGS_SISE[0] // 2) - 50, 245), 4,
                         15)
            pg.draw.rect(settings_window, (255, 127, 39), pg.Rect(15, 15,
                                                                  (self.WINDOW_SETTINGS_SISE[0] // 2) - 210, 245), 4,
                         15)
            pg.draw.rect(settings_window, (255, 127, 39), pg.Rect(25, 35,
                                                                  (self.WINDOW_SETTINGS_SISE[0] // 2) - 230, 85), 4,
                         15)
            pg.draw.rect(settings_window, (255, 127, 39), pg.Rect(25, 140,
                                                                  (self.WINDOW_SETTINGS_SISE[0] // 2) - 230, 105), 4,
                         15)
            pg.draw.line(settings_window, (255, 127, 39), (25, 175), ((self.WINDOW_SETTINGS_SISE[0] // 2) - 210, 175), 4)
            coins_str = str(" " * (7 - len(str(self.user_coins))) + str(self.user_coins))
            max_lxl_str = str(" " * (4 - len(str(self.user_max_lvl))) + str(self.user_max_lvl))
            skill = str(" " * (4 - len(str(self.user_skill))) + str(self.user_skill))
            self.user_coins_lab = self.status_fond.render(f"Монетки:     {coins_str}", True, (180, 0, 0))
            self.user_max_lvl_lab = self.status_fond.render(f"Макс. уровень:{max_lxl_str}", True, (180, 0, 0))
            self.user_skill_lib = self.status_fond.render(f"Проф. уровень:{skill}", True, (180, 0, 0))

            pg.draw.line(settings_window, (255, 127, 39), (25, 210), ((self.WINDOW_SETTINGS_SISE[0] // 2) - 210, 210),4)
            self.in_left_button.draw(settings_window)
            self.in_right_button.draw(settings_window)
            self.tank_im = self.tanks_list[self.tank_index]((375, 50))
            self.tank_im.draw(settings_window, sise_x=1.5)
            settings_window.blit(self.user_name_lab, (110, 65))
            settings_window.blit(self.user_coins_lab, (35, 150))
            settings_window.blit(self.user_max_lvl_lab, (35, 185))
            settings_window.blit(self.user_skill_lib, (35, 215))
            for i in self.levels_buttons:
                i.draw(settings_window)
            for event in pg.event.get():
                self.quit_window(event)

                self.in_left_button.click_or_not_click(event.type)
                self.in_right_button.click_or_not_click(event.type)
                self.user_im_bitton.click_or_not_click(event.type)
                for i in self.levels_buttons:
                    i.click_or_not_click(event.type)
            self.user_im_bitton.draw(settings_window)
            if pg.display.get_init():
                pg.display.flip()

    def open_file_dialog(self, parent: Push_Buttons):
        self.Tk_root.withdraw()
        filename = askopenfilename(filetypes=(("Поддерживаемые файлы изображений", "*.png *.jpg *.jpeg *.bmp *.gif"),),
                                   title="Выберите аватарку")
        if filename != "":
            try:
                im = pg.transform.scale(pg.image.load(filename), (65, 65))
                parent.im = im
                file_type = filename[filename.rfind("."):]
                pg.image.save(im, f"player_image{file_type}")
                con = sql.connect('for_game.db')
                with con:
                    cur = con.cursor()
                    self.user_im_pash = f"player_image{file_type}"

                    chst = str(f"UPDATE player SET im_path='{str(self.user_im_pash)}'")
                    cur.execute(chst)
                con.commit()
                con.close()

            except pg.error:
                tkinter.messagebox.showwarning(title="Ошибка", message="Файл не поддерживаеться или повреждён")


    def init_(self):
        set_game.list_tanks_and_blocks = list()
        set_game.bonus_list = list()
        set_game.hardness_map = list()
        pg.mixer.music.load(r"ogg/intro.ogg")
        pg.mixer_music.play()

        # настройки экрана
        pg.display.set_caption("TANKS")
        pg.display.set_icon(pg.image.load("Tank_im/Icon_tank1_u.png"))
        # # game_card = [["#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
        # #              ["#", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        # #              ["#", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        # #              ["#", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        # #              ["#", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        # #              ["#", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        # #              ["#", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        # #              ["#", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        # #              ["#", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
        # #              ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#"]]
        # game_card = ["##########",
        #              "#        #",
        #              "#        #",
        #              "#        #",
        #              "#        #",
        #              "#        #",
        #              "#  ####  #",
        #              "#        #",
        #              "#        #",
        #              "##########"]
        # список для карты
        self.game_card = list()
        # открываем txt файл с игровой картой
        if self.gamecard == None:
            self.g_c_str = open("Game_card1.txt", "r")
        else:
            self.g_c_str = open(self.gamecard, "r")

        # список со всеми блоками
        self.game_card_blocks = [pg.image.load("Game_card_puzzles\Im_None.png"),
                                 pg.image.load("Game_card_puzzles\Im_Brick_block.png")]
        for i in self.g_c_str:
            self.game_card.append(i[:-1])
        s_t = 0
        self.block_card = []
        # список с 0 и 1 изображающий карту
        hardness_map = []
        # создаём список сэкземплярами класса Blocks
        for i in self.game_card:
            self.block_card.append(list())
            hardness_map.append([])
            s_b = 0
            for s_n in i:
                if s_n == "#":
                    self.block_card[s_t].append(
                        Blocks(self.game_card_blocks[1],
                               (s_b * set_game.delta_tanks_spr, s_t * set_game.delta_tanks_spr), False))
                    hardness_map[s_t].append(1)
                elif s_n == " ":
                    self.block_card[s_t].append(
                        Blocks(self.game_card_blocks[0],
                               (s_b * set_game.delta_tanks_spr, s_t * set_game.delta_tanks_spr), True))
                    hardness_map[s_t].append(0)
                s_b += 1
            s_t += 1

        self.vision_list = list()
        for i in hardness_map:
            self.vision_list += i
        self.hardness_map = hardness_map
        set_game.hardness_map = hardness_map

        self.ran = True
        self.Tank1 = self.tanks_list[self.tank_index]((50, 50))
        # Tank2 = Tanks((50, 650))
        # Tank3 = Tanks((38, 300))
        # # создаём нейросеть
        # n = neuralNetwork(9, 12, 4)
        # # загружаем модель
        # n.dowload_model()
        # # train(n)
        self.window = pg.display.set_mode(set_game.screen_dimensions)
        self.N_tanks = list()
        for k, i in enumerate(self.v_settings):
            _i = i((56, 300,), type_t="e")
            self.N_tanks.append(_i)
            self.N_tanks[k].enemy = self.Tank1
        self.g_c_str.close()
        for i in self.N_tanks:
            i.vision_list = self.vision_list
            i.init_fisic(mode="no")
            i.start_ev()

    # функция отрисовки игровой карты

    def start_game(self, lvl, parent):
        self.lvl = lvl
        con = sql.connect('for_game.db')
        with con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM lvls WHERE Num_lvl={lvl}")
            lvl_setting = cur.fetchall()[0][:5]
            cur.execute(f"SELECT * FROM lvls WHERE Num_lvl={lvl}")
            self.gamecard = cur.fetchall()[0][-2]
            print(self.gamecard, 8)
        con.close()
        self.num_t = sum(lvl_setting)
        self.v_settings = [Gnat_Tanks] * lvl_setting[0] + [Nimble_APC] * lvl_setting[1] + [Die_Hard_Tanks] * lvl_setting[2] + [Compromise_Tanks] * lvl_setting[3] + [Kettlebell_Tanks] * lvl_setting[4]

        self.init_()
        pg.mixer_music.stop()

        self.ran = True
        pg.mixer_music.pause()
        pg.mixer.stop()
        pg.mixer.pause()
        self.run_s = False

        self.run_game()

    def quit_window(self, event):
        if event.type == pg.QUIT:
            pg.display.quit()
            pg.mixer_music.stop()

            self.ran = False
            pg.mixer_music.pause()
            pg.mixer.stop()
            pg.mixer.pause()
            sys.exit(0)
            return

    def drow_card(self, window):
        for i, t in enumerate(self.block_card):
            for n in t:
                n.drow(window)

    def N_tanks_metod_kall(self, metod, args=None, return_values=False):
        return_list = list()
        for i in self.N_tanks:
            f = getattr(i, str(metod))
            if args != None:
                return_list.append(f(*args))
                continue
            return_list.append(f())
        if return_values:
            return return_list

    def init_N(self):
        pass

    # @njit(fastmath=True)
    def run_game(self):
        # def timer_aktiv():
        #     self.ran = False
        #
        #     k = 0
        #
        #     print('эпоха завершена ')
        #
        #     # return
        #     # sys.stderr.close()
        #     os._exit(1)
        #     pg.quit()
        #     pg.mixer_music.stop()
        #
        #     self.ran = False
        #     # self.window.close()
        #     pg.mixer_music.pause()
        #     pg.mixer.stop()
        #     pg.mixer.pause()
        #
        #     # os._exit(os.EX_OK)
        #     def p():
        #         pass
        #
        #     pg.register_quit(p)
        #
        #     sys.exit()

        self.time_lvl = time.time()
        while self.ran:
            #    QtWidgets.QApplication.quit()             # !!! если вы хотите, чтобы событие завершилось

            pg.time.delay(35)
            # sys.stderr = open('errors.log', 'w')
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # return
                    # sys.stderr.close()
                    pg.display.quit()
                    pg.mixer_music.stop()

                    self.ran = False
                    # self.window.close()
                    pg.mixer_music.pause()
                    pg.mixer.stop()
                    pg.mixer.pause()

                    # os._exit(os.EX_OK)
                    def p():
                        pass

                    pg.register_quit(p)
                    os._exit(1)
                    sys.exit()
                    return
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.check_stop_game(True)

                    # raise ValueError

            self.Tank1.init_move(pg.key.get_pressed()[pg.K_SPACE],
                                 fl_right=pg.key.get_pressed()[pg.K_RIGHT],
                                 fl_lelf=pg.key.get_pressed()[pg.K_LEFT],
                                 fl_down=pg.key.get_pressed()[pg.K_DOWN],
                                 fl_up=pg.key.get_pressed()[pg.K_UP])

            # if pg.key.get_pressed()[pg.K_TAB] or T1:
            #     T1 = Tank2.fire()

            # if pg.key.get_pressed()[pg.K_d] and isinstance(Tank2, Tanks):
            #     Tank2.right()
            # elif pg.key.get_pressed()[pg.K_a] and isinstance(Tank2, Tanks):
            #     Tank2.left()
            # elif pg.key.get_pressed()[pg.K_s] and isinstance(Tank2, Tanks):
            #     Tank2.down()
            # elif pg.key.get_pressed()[pg.K_w] and isinstance(Tank2, Tanks):
            #     Tank2.up()

            self.Tank1.init_fisic(mode="kl")
            for i in self.N_tanks:
                i.init_fisic(mode="kl")
                i.init_move(pg.key.get_pressed()[pg.K_TAB],
                            fl_right=pg.key.get_pressed()[pg.K_d],
                            fl_lelf=pg.key.get_pressed()[pg.K_a],
                            fl_down=pg.key.get_pressed()[pg.K_s],
                            fl_up=pg.key.get_pressed()[pg.K_w])
                i.enemy = self.Tank1
                i.update_direction()
            if random.randint(0, 1000) > 997:
                set_game.bonus_list.append(Invulnerability_Bonus((random.randint(0, 860), random.randint(0, 860))))
                # self.window.blit(pg.image.load("Pause or You WIN or You DEAD background.png"),
                # (0, Settings_game().screen_dimensions[1] / 2 - 191 / 2))
                # font = pg.font.SysFont("bahnschrift", 65)
                # font = pg.font.Font(r"fonts\PressStart2P-Regular.ttf", 65)
                # sc_text = font.render("Тебя убили", 1, (255, 100, 0))
                # self.window.blit(sc_text, (50, Settings_game().screen_dimensions[1] / 2 - 191 / 2 + 20))

            self.N_tanks_metod_kall("is_live", return_values=True)
            self.Tank1.size_to_wall()

            self.drow_card(self.window)
            self.Tank1.draw(self.window)
            self.N_tanks_metod_kall("draw", args=[self.window])

            self.vision_list[(self.Tank1.x_and_y[0] + 24) // 48 + (self.Tank1.x_and_y[1] + 24) // 48 * 16] = 5
            Train = True
            for i in self.N_tanks:
                x, y = self.Tank1.x_and_y
                x2, y2 = i.x_and_y

                def fire_may(ob=i.bullet, cl=int):
                    if isinstance(ob, cl):
                        return 1
                    return 0
            for i in set_game.bonus_list:
                i.drow(pg.display.get_surface())
                i.give_effect()
            pg.display.flip()
            print(self.check_stop_game())

    def check_stop_game(self, p=False):
        if self.Tank1.health <= 0:
            print("Пройгрыш")
            self.ran = False
            for i in self.N_tanks:
                i.run_lvl = False
            self.time_lvl = time.time() - self.time_lvl
            # self.coin_take = time.
            con = sql.connect('for_game.db')
            with con:
                cur = con.cursor()
                # cur.execute(f"")
                con.commit()
            con.close()
            miniwin = pg.image.load(r"mini_windows/LOSE_WINDOW.png")
            pg.init()
            base_miniwin_x_and_y = [i // 2 - miniwin.get_size()[n] // 2 for n, i in
                                    enumerate(pg.display.get_window_size())]
            self.IN_MENU_BUTTON = Push_Buttons((base_miniwin_x_and_y[0] + 64, base_miniwin_x_and_y[1] + 175),
                                               pg.image.load(r"mini_windows/IN_MENU_BUTTTON.png"),
                                               lambda parent: self.__init__())
            self.REPLAY_BUTTON = Push_Buttons((base_miniwin_x_and_y[0] + 164, base_miniwin_x_and_y[1] + 175),
                                              pg.image.load(r"mini_windows/REPLAY_BUTTON.png"),
                                              lambda parent: self.start_game(self.lvl, parent=parent))
            while True:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        # return
                        # sys.stderr.close()
                        pg.display.quit()
                        pg.mixer_music.stop()

                        # self.window.close()
                        pg.mixer_music.pause()
                        pg.mixer.stop()
                        pg.mixer.pause()

                        def p():
                            pass

                        pg.register_quit(p)
                        os._exit(1)
                    self.IN_MENU_BUTTON.click_or_not_click(event.type)
                    self.REPLAY_BUTTON.click_or_not_click(event.type)
                self.window.blit(miniwin, base_miniwin_x_and_y)
                self.IN_MENU_BUTTON.draw(pg.display.get_surface())
                self.REPLAY_BUTTON.draw(pg.display.get_surface())
                pg.display.flip()
        elif len([bool(i.health <= 0) for i in set_game.list_tanks_and_blocks if isinstance(i, (Tanks, Kettlebell_Tanks, Gnat_Tanks, Die_Hard_Tanks, Compromise_Tanks, Nimble_APC)) and i is not self.Tank1]) == 0:
            self.ran = False
            print("Победа")
            for i in self.N_tanks:
                    i.run_lvl = False
            self.time_lvl = time.time() - self.time_lvl
            # self.coin_take = time.
            if self.user_max_lvl < self.lvl:
                con = sql.connect('for_game.db')
                with con:
                    cur = con.cursor()
                    cur.execute(f"UPDATE player SET maximum_level_passed='{self.user_max_lvl + 1}'")
                    con.commit()
                con.close()
            miniwin = pg.image.load(r"mini_windows/WIN_WINDOW.png")
            pg.init()
            base_miniwin_x_and_y = [i // 2 - miniwin.get_size()[n] // 2 for n, i in
                                    enumerate(pg.display.get_window_size())]
            self.IN_MENU_BUTTON = Push_Buttons((base_miniwin_x_and_y[0] + 64, base_miniwin_x_and_y[1] + 175),
                                               pg.image.load(r"mini_windows/IN_MENU_BUTTTON.png"), lambda parent: self.__init__())
            self.REPLAY_BUTTON = Push_Buttons((base_miniwin_x_and_y[0] + 155, base_miniwin_x_and_y[1] + 175),
                                               pg.image.load(r"mini_windows/REPLAY_BUTTON.png"), lambda parent: self.start_game(self.lvl ,parent=parent))
            self.NEXT_PLAY_BUTTON = Push_Buttons((base_miniwin_x_and_y[0] + 248, base_miniwin_x_and_y[1] + 175),
                                               pg.image.load(r"mini_windows/NEXT_PLAY_BUTTON.png"), lambda parent: self.start_game(self.lvl + 1 ,parent=parent))
            while True:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        # return
                        # sys.stderr.close()
                        pg.display.quit()
                        pg.mixer_music.stop()


                        # self.window.close()
                        pg.mixer_music.pause()
                        pg.mixer.stop()
                        pg.mixer.pause()

                        def p():
                            pass

                        pg.register_quit(p)
                        os._exit(1)
                    self.IN_MENU_BUTTON.click_or_not_click(event.type)
                    self.REPLAY_BUTTON.click_or_not_click(event.type)
                    self.NEXT_PLAY_BUTTON.click_or_not_click(event.type)
                self.window.blit(miniwin, base_miniwin_x_and_y)
                self.IN_MENU_BUTTON.draw(pg.display.get_surface())
                self.NEXT_PLAY_BUTTON.draw(pg.display.get_surface())
                self.REPLAY_BUTTON.draw(pg.display.get_surface())
                pg.display.flip()
        elif p:
            for i in self.N_tanks:
                    i.run_lvl = False
            miniwin = pg.image.load(r"mini_windows/PAUSE_WINDOW.png")
            pg.init()
            base_miniwin_x_and_y = [i // 2 - miniwin.get_size()[n] // 2 for n, i in
                                    enumerate(pg.display.get_window_size())]
            self.IN_MENU_BUTTON = Push_Buttons((base_miniwin_x_and_y[0] + 64, base_miniwin_x_and_y[1] + 96),
                                               pg.image.load(r"mini_windows/IN_MENU_BUTTTON.png"),
                                               lambda parent: self.__init__())
            self.REPLAY_BUTTON = Push_Buttons((base_miniwin_x_and_y[0] + 155, base_miniwin_x_and_y[1] + 96),
                                              pg.image.load(r"mini_windows/REPLAY_BUTTON.png"),
                                              lambda parent: self.start_game(self.lvl, parent=parent))
            self.PLAY_BUTTON = Push_Buttons((base_miniwin_x_and_y[0] + 248, base_miniwin_x_and_y[1] + 96),
                                                 pg.image.load(r"mini_windows/NEXT_PLAY_BUTTON.png"),
                                                 lambda parent: self.start_game(self.lvl + 1, parent=parent))
            while p:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        # return
                        # sys.stderr.close()
                        pg.display.quit()
                        pg.mixer_music.stop()


                        # self.window.close()
                        pg.mixer_music.pause()
                        pg.mixer.stop()
                        pg.mixer.pause()

                        pg.register_quit(lambda: None)
                        os._exit(1)
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            p = False
                            for i in self.N_tanks:
                                i.run_lvl = True
                    self.IN_MENU_BUTTON.click_or_not_click(event.type)
                    self.REPLAY_BUTTON.click_or_not_click(event.type)
                    self.PLAY_BUTTON.click_or_not_click(event.type)
                self.window.blit(miniwin, base_miniwin_x_and_y)
                self.IN_MENU_BUTTON.draw(pg.display.get_surface())
                self.REPLAY_BUTTON.draw(pg.display.get_surface())
                self.PLAY_BUTTON.draw(pg.display.get_surface())
                pg.display.flip()



if __name__ == "__main__":
    GT = Game_Tanks()
    GT.init_N()
    # GT.ran_play(f=print, f1=app.exec_)
