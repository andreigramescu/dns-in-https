# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys

# chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = '/home/ag1319/chromium/src/out/release/chrome'
# chrome_options.add_argument('--incognito') # cache cleared
# # chrome_options.page_load_strategy = '' # wait for JS to finish
# driver = webdriver.Chrome(options=chrome_options)

# # driver.get("http://xdih.com:5000")
# driver.get("https://andreigramescu.com")

# # navigationStart = driver.execute_script("return window.performance.timing.navigationStart")
# # responseStart = driver.execute_script("return window.performance.timing.responseStart")
# # domComplete = driver.execute_script("return window.performance.timing.domComplete")

# # backendPerformance_calc = responseStart - navigationStart
# # frontendPerformance_calc = domComplete - responseStart

# # print("Back End: %s" % backendPerformance_calc)
# # print("Front End: %s" % frontendPerformance_calc)

# perf_entries = driver.execute_script("return window.performance.getEntries();")
# for entry in perf_entries:
#     print(entry['name'])

# driver.quit()

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests

BINARY_PATH = '/home/ag1319/chromium/src/out/Default/chrome'
DIH_SERVER = 'https://dih-server-83476fffcb63.herokuapp.com'

def create_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = BINARY_PATH
    chrome_options.add_argument('--incognito') # cache cleared
    # chrome_options.page_load_strategy = '' # wait for JS to finish
    return webdriver.Chrome(options=chrome_options)


# response = requests.get(f'{DIH_SERVER}/toggle-dih')
# while ...:
#     response = requests.get(f'{DIH_SERVER}/toggle-dih')

driver = create_driver()
driver.get(DIH_SERVER)

entries = driver.execute_script('return performance.getEntries()')
is_navigation = lambda e: e['entryType'] == 'navigation'
navigation = list(filter(is_navigation, entries))[0]

print(f'Duration is {navigation["duration"]}')

driver.close()
driver.quit()