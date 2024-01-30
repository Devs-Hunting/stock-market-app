from django.test import LiveServerTestCase
from django.urls import reverse
from factories.factories import UserFactory
from selenium import webdriver
from selenium.webdriver.common.by import By


class TestLogIn(LiveServerTestCase):
    """
    End to end browser test of logging user in
    """

    url_name = "account_login"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_url = cls.live_server_url
        cls.password = "pass"
        cls.user = UserFactory(password=cls.password)
        # options = Options()
        # options.add_argument("--headless")
        # options.add_argument("--window-size=1920, 1080")
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Geck"
        #                      "o) Chrome/87.0.4280.88 Safari/537.36")
        # cls.driver = webdriver.Chrome(options=options)
        cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(10)
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
