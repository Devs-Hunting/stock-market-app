from authenticated import AuthenticatedTestCase
from django.urls import reverse
from selenium.webdriver.common.by import By


class TestLogIn(AuthenticatedTestCase):
    """
    End to end browser test of logging user in
    """

    url_name = "account_login"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_url = cls.live_server_url
        cls.url = cls.base_url + reverse(TestLogIn.url_name)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.driver.quit()
        super().tearDownClass()

    def test_should_log_in_user(self):
        self.driver.get(self.url)
        user_email = self.driver.find_element(By.ID, "id_login")
        user_password = self.driver.find_element(By.ID, "id_password")
        user_email.send_keys(self.user.email)
        user_password.send_keys(self.password)
        submit = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit.click()
        self.assertEqual(self.driver.current_url, self.base_url + "/users/profile/")
        cookies_names = [cookie.get("name") for cookie in self.driver.get_cookies()]
        self.assertIn("sessionid", cookies_names)
