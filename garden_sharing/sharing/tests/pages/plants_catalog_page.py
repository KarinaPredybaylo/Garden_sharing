import time

from tms.garden_test.pages.base_page import BasePage
from tms.garden_test.pages.plant_detail_page import PlantDetailPage
from tms.garden_test.pages.plants_catalog_page_locators import PlantsCatalogPageLocators


class PlantsCatalogPage(BasePage):

    def __init__(self, driver, url):
        super().__init__(driver, url)

    def find_plant(self):
        self.driver.find_element(*PlantsCatalogPageLocators.NAME).click()
        time.sleep(2)
        return PlantDetailPage(self.driver, self.driver.current_url)

