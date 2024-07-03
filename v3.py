from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from extras.wordle_unlimited import Wordle_Unlimited as wu2

from time import sleep, time

import constants as c


class Bot:
    def __init__(self, size, pos):
        self.driver = webdriver.Safari()
        self.driver.get("https://wordleunlimited.org")
        self.driver.set_window_size(size[0], size[1])
        self.driver.set_window_position(pos[0], pos[1])
        # remove tutorial
        ActionChains(driver=self.driver).move_by_offset(0, 0).click().perform()

    def do_play(self):
        wordle_unlimited = wu2()
        game = self.driver.find_element(By.TAG_NAME, "game-app")

        for _try in range(c.TRIES):
            guess = wordle_unlimited.best_guess_s
            game.send_keys(f"{guess}\n")

            time_0 = time()

            colors = self.get_colors(letters=guess)
            wordle_unlimited.do_try(guess_s=guess, colors=colors)

            if colors == "22222":
                time_1 = time()
                try:
                    sleep(c.DELAY_REPLAY + c.DELAY_TRY - time_1 + time_0)
                except:
                    pass

                self.driver.execute_script(
                    f"""return document.querySelector('game-app').shadowRoot.querySelector('game-stats').shadowRoot.querySelector('button[id="refresh-button"]')"""
                ).click()
                return _try

            time_1 = time()
            try:
                sleep(c.DELAY_TRY - time_1 + time_0)
            except:
                pass

        return c.TRIES + 1

    def get_colors(self, letters):
        raw_colors = [
            raw_color.get_attribute("outerHTML")
            for raw_color in self.driver.execute_script(
                f"""return document.querySelector('game-app').shadowRoot.querySelector('game-row[letters="{letters}"]').shadowRoot.querySelectorAll('game-tile[letter]')"""
            )
        ]

        colors = ""
        for raw_color in raw_colors:
            if "absent" in raw_color:
                colors += "0"
            elif "present" in raw_color:
                colors += "1"
            elif "correct" in raw_color:
                colors += "2"
        return colors

    def __del__(self):
        print("\nthanks for playing!\n")
        self.driver.quit()


if __name__ == "__main__":
    bot = Bot(size=(c.SCREEN_SIZE[0], c.SCREEN_SIZE[1]), pos=(0, 0))

    try:
        while True:
            sleep(0.5)
            bot.do_play()

    except:
        print("error")

    del bot
