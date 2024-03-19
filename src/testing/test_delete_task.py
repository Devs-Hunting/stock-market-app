import re
import time

import pytest  # noqa
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .settings import TEST_HOST

pytest_plugins = [
    "testing.fixtures.authenticated",
]


def get_status_from_task_html(task_html):
    return task_html.find_element(By.XPATH, "//a[1]//div//div//p").text


def test_should_delete_task(authenticated_test):
    driver, test_user = authenticated_test
    task_list_url = TEST_HOST + "/tasks/"
    task_url_pattern = r"\/tasks\/[0-9]+$"
    task_delete_url_pattern = r"\/tasks\/[0-9]+/delete$"

    # navigate
    navbar_tasks = driver.find_element(By.ID, "navbar-tasks")
    navbar_tasks.click()
    navbar_create_task = driver.find_element(By.ID, "navbar-tasks-list")
    navbar_create_task.click()

    assert task_list_url in driver.current_url

    # open first task from the list that has OPEN status
    tasks_list = driver.find_element(By.ID, "tasks-list")
    tasks = tasks_list.find_elements(By.TAG_NAME, "li")
    task_to_delete = None
    task_id = None
    for task in tasks:
        status = get_status_from_task_html(task)
        if status == "Status: open":
            task_to_delete = task
            task_id = task.get_property("id")
            break

    if not task_to_delete:
        return

    # redirect to task
    task_link = task_to_delete.find_element(By.XPATH, ".//a[1]")
    task_link.click()
    time.sleep(2)
    match = re.search(task_url_pattern, driver.current_url)
    assert bool(match)

    # redirect to confirmation
    task_delete = driver.find_element(By.ID, "task-delete")
    task_delete.click()
    time.sleep(2)
    match = re.search(task_delete_url_pattern, driver.current_url)

    # delete task
    submit = driver.find_element(By.ID, "confirm-delete-task")
    submit.click()
    time.sleep(2)
    # redirect to list
    assert task_list_url in driver.current_url
    with pytest.raises(NoSuchElementException):
        driver.find_element(By.ID, task_id)
