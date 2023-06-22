from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests

BINARY_PATH = '/home/ag1319/chromium/src/out/release/chrome'
DIH_SERVER = 'https://dih-server-83476fffcb63.herokuapp.com'

def create_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = BINARY_PATH
    chrome_options.add_argument('--incognito') # cache cleared
    return webdriver.Chrome(options=chrome_options)

driver = create_driver()
driver.get(DIH_SERVER)
entries = driver.execute_script('return performance.getEntries()')
is_navigation = lambda e: e['entryType'] == 'navigation'
navigation = list(filter(is_navigation, entries))[0]

print(f'Duration with DiH header on is: {navigation["duration"]}')
driver.close()
driver.quit()


driver = create_driver()
driver.get(DIH_SERVER + "/no-dih-header")
entries = driver.execute_script('return performance.getEntries()')
is_navigation = lambda e: e['entryType'] == 'navigation'
navigation = list(filter(is_navigation, entries))[0]

print(f'Duration with DiH header off is: {navigation["duration"]}')
driver.close()
driver.quit()
