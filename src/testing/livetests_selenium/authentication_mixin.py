from django.urls import reverse
from factories.factories import UserFactory
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class MultiUserAuthenticatedTestCaseMixin:
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.password = "pass"
        cls.options = Options()
        cls.options.add_argument("--headless")
        cls.options.add_argument("--start-maximized")
        cls.options.add_argument("--window-size=1920, 1080")
        cls.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Geck"
            "o) Chrome/87.0.4280.88 Safari/537.36"
        )

    def setUp(self) -> None:
        self.login_url = self.live_server_url + reverse("account_login")
        self.users_dict = {}
        for i in range(self.NB_OF_TEST_USERS):
            self.users_dict[i] = {}
            self.users_dict[i]["instance"] = UserFactory(password=self.password)
            self.users_dict[i]["driver"] = webdriver.Chrome(options=self.options)
            # self.users_dict[i]["driver"] = webdriver.Chrome()
            self.users_dict[i]["driver"].implicitly_wait(10)
            self.users_dict[i]["driverwait"] = WebDriverWait(self.users_dict[i]["driver"], 10)
            self.login_user(self.users_dict[i]["instance"], self.users_dict[i]["driver"])

    def tearDown(self) -> None:
        for k in self.users_dict.keys():
            self.users_dict[k]["driver"].quit()

    def login_user(self, usr, dvr):
        dvr.get(self.login_url)
        user_email = dvr.find_element(By.ID, "id_login")
        user_password = dvr.find_element(By.ID, "id_password")
        user_email.send_keys(usr.email)
        user_password.send_keys(self.password)
        submit = dvr.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit.click()
