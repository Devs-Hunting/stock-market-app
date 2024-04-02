from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_driver():
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920, 1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Geck"
        "o) Chrome/87.0.4280.88 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver
