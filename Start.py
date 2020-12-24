import time
import json
from datetime import datetime
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options as Chrome_options
from Building import Building
from Utils import wait,wait_until,click,pressEscape,dated_message,string_to_delta_time,date_to_string,click_ac
import Events
import Files
import Game


def load_init_actions(game):

    if(game.settings['player']['reapVillages']):
        if(game.settings['player']['captain']):
            game.add_action(datetime.now(),game.village_loot_captain,None)
        else:
            game.add_action(datetime.now(),game.village_loot,None)

    if(game.settings['player']['culture']):
        if(game.settings['player']['admin']):
            game.add_action(datetime.now(),game.culture,None)

    for currentCity in game.cities:
            if(game.settings['player']['manageSenate']):
                game.add_action(datetime.now(),game.upgrade_buildings,currentCity)

            if(game.settings['player']['academy']):
                game.add_action(datetime.now(),game.academy,currentCity)

    if(game.settings['player']['max_hours_to_run'] != 0.0):
        deltaTime = timedelta(minutes=int(game.settings['player']['max_hours_to_run']))
        newTime = datetime.now()+deltaTime
        game.add_action(newTime,game.end,None)




def play_grepolis(flag, update_function, finish_function):
    
    queue = Events.ActionsQueue()
    files = Files.Files("settings.json","log.txt")
    # Start browser and login
    browser = execute_game_session(files.get_settings(), flag, update_function)

    game = Game.Game(browser,files,queue,flag,update_function,finish_function)

    game.load_settings()

    try:

        game.get_cities()

        load_init_actions(game)

        while 1:
            if(game.do_next_action() == 1):
                break
            

    except Exception as e:
        print('Something went wrong:')
        print(e)
        game.end()



# logs in, manages the game and closes the browser
def execute_game_session(settings, flag, update_function):

    # setup web browser
    exePath = settings['webDriver']["executablePath"]
    try:
        browser = webdriver.Chrome(exePath)
    except Exception as e:
        print(e)
        print('Failed to start webdriver.')
        flag.set(True)
        return

    browser.maximize_window()
    try:
        update_function('Logging in')
        login_and_select_world(browser, settings['player'])

    except Exception as e:
        print(e)
        browser.quit()
        print('Something went wrong in the login.')

    return browser




# logs the user in and navigates to the game world
def login_and_select_world(browser,player):
    #browser.maximize_window()
    browser.get(player['server'])
    time.sleep(1)

    # find username and password inputs
    usernameInput = browser.find_element_by_id('login_userid')
    passwordInput = browser.find_element_by_id('login_password')

    # enter user name and password
    usernameInput.send_keys(player['username'])
    time.sleep(1)
    passwordInput.send_keys(player['password'])
    time.sleep(1)

    #press login button
    loginButton = browser.find_element_by_id('login_Login')
    loginButton.click()
    time.sleep(5)

    #select world
    worldButton = browser.find_elements_by_class_name('world_name')
    worldButton[player['world_number']].find_element_by_css_selector('div').click()
    time.sleep(2)

    # exit any pop ups
    pressEscape(browser)
    time.sleep(1)
    pressEscape(browser)
