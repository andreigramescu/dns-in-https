from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests

BINARY_PATH = '/home/ag1319/chromium/src/out/release/chrome'
DIH_SERVER = 'https://dih-server-83476fffcb63.herokuapp.com'

SUCCESS = True

domains = ["www.example.com",
           "www.andreigramescu.com",
           "www.imperial.ac.uk",
           "en.wikipedia.org",
           "www.imperial.ac.uk",
           "public.nftstatic.com",
           "tfl.gov.uk"]

def create_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = BINARY_PATH
    chrome_options.add_argument('--incognito') # cache cleared
    return webdriver.Chrome(options=chrome_options)

driver = create_driver()
driver.get(DIH_SERVER)
driver.close()
driver.quit()

cache = requests.get(DIH_SERVER + "/cache").json()
for domain in domains:
    SUCCESS = SUCCESS and (domain not in cache)

if not SUCCESS:
    print("After loading the page with the DiH header, some of the entries were not cached")
    exit(1)

driver = create_driver()
driver.get(DIH_SERVER + "/no-dih-header")
driver.close()
driver.quit()

cache = requests.get(DIH_SERVER + "/cache").json()
for domain in domains:
    SUCCESS = SUCCESS and (domain in cache)

if not SUCCESS:
    print("After loading the page with dynamic DiH, some of the queries were not made to the server")
    exit(1)

print("Tests succeeded")