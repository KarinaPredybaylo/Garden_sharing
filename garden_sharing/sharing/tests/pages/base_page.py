from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver, url):
        self.driver = driver
        self.url = url

    def open_page(self):
        self.driver.get(self.url)

    def find_element(self, locator):
        element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(locator),
                                                           message=f"Can't find element by locator {locator}")
        return element
