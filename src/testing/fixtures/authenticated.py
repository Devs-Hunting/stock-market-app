import pytest
from selenium.webdriver.common.by import By

from ..driver import create_driver
from ..settings import TEST_HOST


def login(driver, user):
    login_endpoint = "/users/accounts/login/"
    login_url = TEST_HOST + login_endpoint
    driver.get(login_url)
    user_email = driver.find_element(By.ID, "id_login")
    user_password = driver.find_element(By.ID, "id_password")
    user_email.send_keys(user["email"])
    user_password.send_keys(user["password"])
    submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit.click()


@pytest.fixture()
def selenium_test():
    driver = create_driver()
    return driver


@pytest.fixture()
def authenticated_test(selenium_test):
    # setup
    driver = selenium_test
    test_user = {"email": "user_1@example.com", "password": "secret"}
    login(driver, test_user)
    # test
    yield driver, test_user
    # teardown
    driver.quit()
