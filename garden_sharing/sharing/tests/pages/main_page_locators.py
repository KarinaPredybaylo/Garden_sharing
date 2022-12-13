from selenium.webdriver.common.by import By


class MainPageLocators:
    LOGIN_LOCATOR = (By.XPATH, "//b[text()='   Log In']")
    WISH_LIST_LOCATOR = (By.XPATH, "//a[text()='Wish list']")
    CATALOG = (By.XPATH, "//li[@class='has-children']")
    PLANT_CATALOG_LOCATOR = (By.XPATH, "//a[text()='Plants']")

