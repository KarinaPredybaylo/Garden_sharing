from tms.garden_test.pages.base_page import BasePage
from tms.garden_test.pages.login_page_locators import LoginPageLocators


class LoginPage(BasePage):
    URL = 'http://127.0.0.1:8000/register/login/'

    def __init__(self, driver):
        super().__init__(driver, self.URL)

    def login(self, username, password):
        self.driver.find_element(*LoginPageLocators.EMAIL).send_keys(username)
        self.driver.find_element(*LoginPageLocators.PASSWORD).send_keys(password)
        self.driver.find_element(*LoginPageLocators.SUBMIT).submit()
