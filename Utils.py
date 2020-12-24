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


def wait(seconds, flag):
    return_time = datetime.now() + timedelta(seconds=seconds)
    while datetime.now() < return_time and flag.get() == False:
        time.sleep(1)

def wait_until(date):
    while datetime.now() < date:
        time.sleep(1)

def parse_seconds(string):
    minutes = 'hours' not in string
    number_minutes = int(string.strip('minutes').strip('hours').strip(' '))
    if minutes == False:
        number_minutes *= 60

    return 60 * number_minutes

def click(webElement):
    webElement.click()
    time.sleep(1)

def click_ac(browser,webElement):
    ac = ActionChains(browser)
    ac.move_to_element(webElement).move_by_offset(0, 0).click().perform()
    time.sleep(1)

def pressEscape(browser):
    browser.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
    time.sleep(1)

def string_date():
    date = datetime.now()
    s = str(date.hour) + ":" + (str(date.minute) if len(str(date.minute)) == 2 else '0' + str(date.minute))
    return s

def dated_message(message):
    print(string_date(),": ",message)

def string_to_delta_time(dateStr):
    dateStr = dateStr.split(":")
    #print(dateStr)
    return timedelta(hours = int(dateStr[0]), minutes = int(dateStr[1]), seconds = int(dateStr[2]))

# Given a date it returns the string format of the date.
def date_to_string(date):
    return (str(date.hour) + ":" + str(date.minute))
