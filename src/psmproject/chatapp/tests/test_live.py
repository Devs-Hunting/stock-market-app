from chatapp.models import PrivateChat, TaskChat
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from factories.factories import (
    ChatFactory,
    ChatParticipantFactory,
    OfferFactory,
    TaskFactory,
    UserFactory,
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

User = get_user_model()


class AuthenticatedTestCase(StaticLiveServerTestCase):
    """
    Live test that logs user in
    """

    login_url_name = "account_login"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.password = "pass"
        # cls.user = UserFactory(password=cls.password)
        cls.options = Options()
        cls.options.add_argument("--headless")
        cls.options.add_argument("--start-maximized")
        cls.options.add_argument("--window-size=1920, 1080")
        cls.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Geck"
            "o) Chrome/87.0.4280.88 Safari/537.36"
        )
        cls.driver = webdriver.Chrome(options=cls.options)
        # cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.login_url = cls.live_server_url + reverse(AuthenticatedTestCase.login_url_name)

    def setUp(self) -> None:
        self.user = UserFactory(password=self.password)
        self.login()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()

    def login(self):
        self.driver.get(self.login_url)
        user_email = self.driver.find_element(By.ID, "id_login")
        user_password = self.driver.find_element(By.ID, "id_password")
        user_email.send_keys(self.user.email)
        user_password.send_keys(self.password)
        submit = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit.click()


class TestChatLive(AuthenticatedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.task = TaskFactory(client=self.user)
        self.offer = OfferFactory(task=self.task)
        self.task_test_private_chat = TaskFactory(client=self.user)

    def tearDown(self):
        while len(self.driver.window_handles) > 1:
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def test_should_create_task_related_chat_when_client_select_offer(self):
        """
        Test that verifies if a chat related to a task is created when the client selects an offer.
        It also checks if the link to the task chat is displayed in the related task view.
        """
        offer_url = reverse("offer-detail", args=[self.offer.id])
        self.driver.get(self.live_server_url + offer_url)
        accept_offer_elem = self.driver.find_element(By.CSS_SELECTOR, "button[data-bs-target='#OfferAcceptModal'")
        accept_offer_elem.click()
        confirm_accept_offer_elem = self.driver.find_element(By.CSS_SELECTOR, "#OfferAcceptModal input[type='submit']")
        confirm_accept_offer_elem.click()
        task_chat = (
            TaskChat.objects.filter(participants__user=self.user)
            .filter(participants__user=self.offer.contractor)
            .first()
        )
        self.assertTrue(task_chat)
        self.assertEqual(task_chat.object_id, self.task.id)
        task_url = reverse("task-detail", args=[self.task.id])
        self.driver.get(self.live_server_url + task_url)
        chat_btn_elems = self.driver.find_elements(By.CLASS_NAME, "chat_link")
        self.assertEqual(len(chat_btn_elems), 1)
        self.assertEqual(int(chat_btn_elems[0].get_attribute("chat_id")), task_chat.id)

    def test_should_should_create_private_chat_when_chat_does_not_exist_yet(self):
        """
        Test that verifies if a private chat is created when the chat does not exist yet.
        It checks if a new browser window is opened with the title "Private chat" and if the URL is correct.
        """
        offer_without_private_chat = OfferFactory(task=self.task_test_private_chat)
        offer_url = reverse("offer-detail", args=[offer_without_private_chat.pk])
        self.driver.get(self.live_server_url + offer_url)
        self.assertEqual(len(self.driver.window_handles), 1)
        contact_user_link = self.driver.find_element(By.CLASS_NAME, "chat_link")
        contact_user_link.click()
        original_window = self.driver.current_window_handle
        self.wait.until(EC.number_of_windows_to_be(2))
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                break
        self.assertEqual(self.driver.title, "Private chat")
        new_chat = (
            PrivateChat.objects.filter(participants__user=self.user)
            .filter(participants__user=offer_without_private_chat.contractor)
            .first()
        )
        self.assertTrue(new_chat)
        self.assertIn(reverse("chat", args=[new_chat.id]), self.driver.current_url)

    def test_should_should_create_private_chat_when_chat_already_exists(self):
        """
        Test that verifies if the user is redirected to an existing private chat when it already exists.
        It checks if a new browser window is opened with the title "Private chat" and if the URL is correct.
        """
        offer_with_private_chat = OfferFactory(task=self.task_test_private_chat)
        existing_private_chat = ChatFactory()
        user_participants = [self.user, offer_with_private_chat.contractor]
        for u in user_participants:
            ChatParticipantFactory(user=u, chat=existing_private_chat)
        offer_url = reverse("offer-detail", args=[offer_with_private_chat.pk])
        self.driver.get(self.live_server_url + offer_url)
        self.assertEqual(len(self.driver.window_handles), 1)
        contact_user_link = self.driver.find_element(By.CLASS_NAME, "chat_link")
        contact_user_link.click()
        original_window = self.driver.current_window_handle
        self.wait.until(EC.number_of_windows_to_be(2))
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                break
        self.assertEqual(self.driver.title, "Private chat")
        self.assertIn(reverse("chat", args=[existing_private_chat.id]), self.driver.current_url)
