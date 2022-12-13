import time

from Plants_share.garden_sharing.sharing.tests.pages.base_page import BasePage
from Plants_share.garden_sharing.sharing.tests.pages.plant_detail_page import PlantDetailPage
from Plants_share.garden_sharing.sharing.tests.pages.plants_catalog_page_locators import PlantsCatalogPageLocators


class PlantsCatalogPage(BasePage):

    def __init__(self, driver, url):
        super().__init__(driver, url)

    def find_plant(self):
        self.driver.find_element(*PlantsCatalogPageLocators.NAME).click()
        time.sleep(2)
        return PlantDetailPage(self.driver, self.driver.current_url)

