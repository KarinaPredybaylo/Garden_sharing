from Plants_share.garden_sharing.sharing.tests.pages.base_page import BasePage
from Plants_share.garden_sharing.sharing.tests.pages.plant_detail_page_locators import PlantsDetailPageLocators


class PlantDetailPage(BasePage):

    def __init__(self, driver, url):
        super().__init__(driver, url)

    def get_image(self):
        return self.driver.find_element(*PlantsDetailPageLocators.PLANT_IMAGE)
