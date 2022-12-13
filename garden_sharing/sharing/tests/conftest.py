import pytest
from selenium import webdriver


# @pytest.fixture(scope='module')
# def driver():
#     driver = webdriver.Chrome()
#     driver.maximize_window()
#     yield driver
#     driver.quit()


@pytest.fixture(scope='module')
def driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.maximize_window()
    # driver.implicitly_wait(5)
    yield driver
    driver.quit()
