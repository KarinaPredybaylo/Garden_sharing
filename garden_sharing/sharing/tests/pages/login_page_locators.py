from selenium.webdriver.common.by import By


class LoginPageLocators:
    EMAIL = (By.XPATH, "//input[@name='username']")
    PASSWORD = (By.XPATH, "//input[@name='password']")
    SUBMIT = (By.XPATH, "//button[text()='SIGN IN']")
