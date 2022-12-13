import time
from Plants_share.garden_sharing.sharing.tests.pages.main_page import MainPage


def test_open_login(driver):
    page = MainPage(driver)
    page.open_page()
    login_page = page.open_login_page()
    login_page.login('karinadurko5@gmail.com', 'Relapse2-')

    assert '/sharing/' in driver.current_url


def test_open_wish_list(driver):
    page = MainPage(driver)
    page.open_page()
    page.open_wish_list_page()

    assert '/requestthing_list' in driver.current_url


def test_open_plant_catalog(driver):
    page = MainPage(driver)
    page.open_page()
    time.sleep(2)
    catalog = page.open_plants_catalog_page()
    time.sleep(2)
    plant = catalog.find_plant()
    time.sleep(2)

    assert 'sharing/plant/' in driver.current_url
    assert plant.get_image()


