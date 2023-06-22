from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import random
from selenium.webdriver.common.keys import Keys

pip install selenium

chrome = webdriver.Chrome(ChromeDriverManager().install())
chrome.get("https://web.whatsapp.com")

search_box = chrome.find_element_by_class_name("_13NKt")
search_box.send_keys("995lyceen2020")
search_box.send_keys(Keys.ENTER)

search_box = chrome.find_element_by_xpath("//div[contains(@class,'copyable-text selectable-text')]")
search_box.send_keys("995lyceen2020")
search_box.send_keys(Keys.ENTER)

boutonJoindre = chrome.find_element_by_xpath("//div[@role='button'][@title='Joindre']")
boutonJoindre.click()

image_box = chrome.find_elements_by_xpath("//button[span/@data-testid='attach-image']")[0]
print(str(image_box))
image_box.click()
input_box = chrome.find_element_by_tag_name('input')
file_path = '/media/jean-christophe/DE70CC3E70CC1EE1/Users/jccar/Pictures/2021/01-janvier/20210117_164617(1).jpg'
input_box.send_keys(file_path)

import time
time.sleep(2)

but = chrome.find_element_by_xpath("//div[@role='button'][span/@data-testid='send']")
but.click()
