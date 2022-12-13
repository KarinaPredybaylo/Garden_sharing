import time
from Plants_share.garden_sharing.sharing.tests.pages.base_page import BasePage
from Plants_share.garden_sharing.sharing.tests.pages.login_page import LoginPage
from Plants_share.garden_sharing.sharing.tests.pages.main_page_locators import MainPageLocators
from Plants_share.garden_sharing.sharing.tests.pages.plants_catalog_page import PlantsCatalogPage


class MainPage(BasePage):
    URL = 'http://127.0.0.1:8000/sharing/'

    def __init__(self, driver):
        super().__init__(driver, self.URL)

    def open_login_page(self):
        login_page = self.driver.find_element(*MainPageLocators.LOGIN_LOCATOR)
        login_page.click()
        return LoginPage(self.driver)

    def open_wish_list_page(self):
        wish_list_page = self.driver.find_element(*MainPageLocators.WISH_LIST_LOCATOR)
        wish_list_page.click()

    def open_plants_catalog_page(self):
        catalog = self.driver.find_element(*MainPageLocators.CATALOG)
        time.sleep(1)
        catalog.click()
        self.driver.find_element(*MainPageLocators.PLANT_CATALOG_LOCATOR).click()
        time.sleep(1)
        return PlantsCatalogPage(self.driver, self.driver.current_url)
