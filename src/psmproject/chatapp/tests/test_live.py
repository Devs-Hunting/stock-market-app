import time
from itertools import chain
from random import randint

from channels.testing import ChannelsLiveServerTestCase
from chatapp.models import Participant, PrivateChat, TaskChat
from chatapp.views import ChatListView
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.db.models import Q
from django.urls import reverse
from factories.factories import (
    ChatFactory,
    ChatParticipantFactory,
    ComplaintChatFactory,
    MessageFactory,
    OfferFactory,
    TaskChatFactory,
    TaskFactory,
)
from factory.fuzzy import FuzzyText
from faker import Faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tasksapp.tests.live.authentication_mixin import AuthenticatedTestCaseMixin

User = get_user_model()

fake = Faker()


class TestChatViewsLive(AuthenticatedTestCaseMixin, StaticLiveServerTestCase):
    NB_OF_TEST_USERS = 1

    def setUp(self) -> None:
        super().setUp()
        self.task = TaskFactory(client=self.users_dict[0]["instance"])
        self.offer = OfferFactory(task=self.task)
        self.task_test_private_chat = TaskFactory(client=self.users_dict[0]["instance"])

    def test_should_create_task_related_chat_when_client_select_offer(self):
        """
        Test that verifies if a chat related to a task is created when the client selects an offer.
        It also checks if link to the task chat is displayed in the related task view and if chat opens correctly in
        new window.
        """
        offer_url = reverse("offer-detail", args=[self.offer.id])
        self.users_dict[0]["driver"].get(self.live_server_url + offer_url)
        self.users_dict[0]["driver"].find_element(By.CSS_SELECTOR, "button[data-bs-target='#OfferAcceptModal'").click()
        self.users_dict[0]["driver"].find_element(By.CSS_SELECTOR, "#OfferAcceptModal input[type='submit']").click()
        task_chat = (
            TaskChat.objects.filter(participants__user=self.users_dict[0]["instance"])
            .filter(participants__user=self.offer.contractor)
            .first()
        )
        self.assertTrue(task_chat)
        self.assertEqual(task_chat.object_id, self.task.id)
        task_url = reverse("task-detail", args=[self.task.id])
        self.users_dict[0]["driver"].get(self.live_server_url + task_url)
        chat_btn_elems = self.users_dict[0]["driver"].find_elements(By.CLASS_NAME, "chat_link")
        self.assertEqual(len(chat_btn_elems), 1)
        self.assertEqual(int(chat_btn_elems[0].get_attribute("chat_id")), task_chat.id)
        chat_btn_elems[0].click()
        original_window = self.users_dict[0]["driver"].current_window_handle
        self.users_dict[0]["driverwait"].until(EC.number_of_windows_to_be(2))
        for window_handle in self.users_dict[0]["driver"].window_handles:
            if window_handle != original_window:
                self.users_dict[0]["driver"].switch_to.window(window_handle)
                break
        self.assertEqual(self.users_dict[0]["driver"].title, f"Task: {self.task.title} - Chat")
        self.assertIn(reverse("chat", args=[task_chat.id]), self.users_dict[0]["driver"].current_url)

    def test_should_should_create_private_chat_when_chat_does_not_exist_yet(self):
        """
        Test that verifies if a private chat is created when the chat does not exist yet.
        It checks if a new browser window is opened with the title "Private chat" and if the URL is correct.
        """
        offer_without_private_chat = OfferFactory(task=self.task_test_private_chat)
        offer_url = reverse("offer-detail", args=[offer_without_private_chat.pk])
        self.users_dict[0]["driver"].get(self.live_server_url + offer_url)
        self.assertEqual(len(self.users_dict[0]["driver"].window_handles), 1)
        self.users_dict[0]["driver"].find_element(By.CLASS_NAME, "chat_link").click()
        original_window = self.users_dict[0]["driver"].current_window_handle
        self.users_dict[0]["driverwait"].until(EC.number_of_windows_to_be(2))
        for window_handle in self.users_dict[0]["driver"].window_handles:
            if window_handle != original_window:
                self.users_dict[0]["driver"].switch_to.window(window_handle)
                break
        self.assertEqual(self.users_dict[0]["driver"].title, "Private chat")
        new_chat = (
            PrivateChat.objects.filter(participants__user=self.users_dict[0]["instance"])
            .filter(participants__user=offer_without_private_chat.contractor)
            .first()
        )
        self.assertTrue(new_chat)
        self.assertIn(reverse("chat", args=[new_chat.id]), self.users_dict[0]["driver"].current_url)

    def test_should_should_create_private_chat_when_chat_already_exists(self):
        """
        Test that verifies if the user is redirected to an existing private chat when it already exists.
        It checks if a new browser window is opened with the title "Private chat" and if the URL is correct.
        """
        offer_with_private_chat = OfferFactory(task=self.task_test_private_chat)
        existing_private_chat = ChatFactory()
        user_participants = [self.users_dict[0]["instance"], offer_with_private_chat.contractor]
        for u in user_participants:
            ChatParticipantFactory(user=u, chat=existing_private_chat)
        offer_url = reverse("offer-detail", args=[offer_with_private_chat.pk])
        self.users_dict[0]["driver"].get(self.live_server_url + offer_url)
        self.assertEqual(len(self.users_dict[0]["driver"].window_handles), 1)
        self.users_dict[0]["driver"].find_element(By.CLASS_NAME, "chat_link").click()
        original_window = self.users_dict[0]["driver"].current_window_handle
        self.users_dict[0]["driverwait"].until(EC.number_of_windows_to_be(2))
        for window_handle in self.users_dict[0]["driver"].window_handles:
            if window_handle != original_window:
                self.users_dict[0]["driver"].switch_to.window(window_handle)
                break
        self.assertEqual(self.users_dict[0]["driver"].title, "Private chat")
        self.assertIn(reverse("chat", args=[existing_private_chat.id]), self.users_dict[0]["driver"].current_url)

    def test_should_return_number_of_elements_and_pages_in_chat_lists_as_per_category(self):
        """
        This test verifies the pagination and count of chat elements for different chat categories including task
        chats, complaint chats, private chats and all chats. It navigates to chat list pages and checks if every page
        displays the correct number of chats and pages.
        It also checks if correct chats are return on view when searching for specific contact.
        """
        chats = {
            "Task chats": TaskChatFactory.create_batch(randint(1, 10)),
            "Complaint chats": ComplaintChatFactory.create_batch(randint(1, 10)),
            "Private chats": ChatFactory.create_batch(randint(1, 10)),
        }
        chats["All chats"] = list(chain.from_iterable(chats.values()))
        for chat in chats["All chats"]:
            ChatParticipantFactory(user=self.users_dict[0]["instance"], chat=chat)
            ChatParticipantFactory(chat=chat)
            MessageFactory(chat=chat, author=self.users_dict[0]["instance"])
        dashboard_url = reverse("dashboard")
        for chat_view in chats.keys():
            self.users_dict[0]["driver"].get(self.live_server_url + dashboard_url)
            self.users_dict[0]["driver"].find_element(By.LINK_TEXT, "Chats").click()
            self.users_dict[0]["driver"].find_element(By.LINK_TEXT, chat_view).click()
            self.assertEqual(self.users_dict[0]["driver"].find_element(By.CSS_SELECTOR, "h2").text, chat_view)
            nb_of_full_pgs, nb_of_elem_on_last_pg = divmod(len(chats[chat_view]), ChatListView.paginate_by)
            last_page_nb = nb_of_full_pgs + 1 if nb_of_elem_on_last_pg else nb_of_full_pgs
            if nb_of_full_pgs > 1:
                pagination_expected_text = f"Page 1 of {last_page_nb}"
                pagination_current_text = self.users_dict[0]["driver"].find_element(By.CLASS_NAME, "current").text
                self.assertEqual(pagination_current_text, pagination_expected_text)
            if nb_of_elem_on_last_pg:
                self.users_dict[0]["driver"].get(f"{self.users_dict[0]['driver'].current_url}?page={last_page_nb}")
                chat_elems = self.users_dict[0]["driver"].find_elements(By.CLASS_NAME, "chat_link")
                self.assertEqual(len(chat_elems), nb_of_elem_on_last_pg)
        all_chats_url = reverse("all-chats")
        self.users_dict[0]["driver"].get(self.live_server_url + all_chats_url)
        self.users_dict[0]["contact_search_field"] = self.users_dict[0]["driver"].find_element(By.ID, "id_contact_name")
        other_participants = Participant.objects.filter(~Q(user=self.users_dict[0]["instance"]))
        rand_particpant_idx = randint(0, len(other_participants) - 1)
        participant_username = other_participants.get(pk=rand_particpant_idx).user.username
        self.users_dict[0]["contact_search_field"].send_keys(participant_username)
        self.users_dict[0]["contact_search_field"].submit()
        chat_link_title = self.users_dict[0]["driver"].find_element(By.CLASS_NAME, "card-title").text
        self.assertIn(participant_username, chat_link_title)


class TestChatCommunicationLive(AuthenticatedTestCaseMixin, ChannelsLiveServerTestCase):
    NB_OF_TEST_USERS = 2

    def setUp(self) -> None:
        super().setUp()
        self.chat = ChatFactory()
        for k in self.users_dict.keys():
            ChatParticipantFactory(user=self.users_dict[k]["instance"], chat=self.chat)
        self.messages = MessageFactory.create_batch(25, chat=self.chat, author=self.users_dict[0]["instance"])

    def test_chat_communication(self):
        """
        This test verifies communication between 2 users in a chat, it also checks if message history is loading
        correctly when user requests it, messages of more than 500 characters are truncated and empty message are not
        sent.
        """
        chat_url = self.live_server_url + reverse("chat", args=[self.chat.id])
        for k in self.users_dict.keys():
            self.users_dict[k]["driver"].get(chat_url)
            self.users_dict[k]["load_msg_btn"] = self.users_dict[k]["driver"].find_element(By.ID, "load-messages")
            self.users_dict[k]["chat_history_count"] = self.users_dict[k]["driver"].find_element(
                By.ID, "chat-history-count"
            )
            self.users_dict[k]["message_input"] = self.users_dict[k]["driver"].find_element(By.ID, "chat-message-input")
            self.users_dict[k]["submit_btn"] = self.users_dict[k]["driver"].find_element(By.ID, "chat-message-submit")
        user1, user2 = self.users_dict.keys()
        for i in range(10, len(self.messages), 10):
            user1_nb_of_msg_not_loaded = int(self.users_dict[user1]["chat_history_count"].text)
            self.assertEqual(user1_nb_of_msg_not_loaded, len(self.messages) - i)
            self.users_dict[user1]["load_msg_btn"].click()
            time.sleep(1)
        self.assertFalse(self.users_dict[user1]["load_msg_btn"].is_displayed())
        self.assertTrue(self.users_dict[user2]["load_msg_btn"].is_displayed())
        self.users_dict[user1]["chat_history_count"] = self.users_dict[user2]["driver"].find_element(
            By.ID, "chat-history-count"
        )
        user2_nb_of_msg_not_loaded = int(self.users_dict[user2]["chat_history_count"].text)
        self.assertEqual(user2_nb_of_msg_not_loaded, len(self.messages) - 10)
        nb_of_new_msg = 4
        messages = [fake.word() for _ in range(nb_of_new_msg)]
        for i, m in enumerate(messages):
            self.users_dict[i % 2]["message_input"].send_keys(m)
            self.users_dict[i % 2]["submit_btn"].click()
            for k in self.users_dict.keys():
                self.users_dict[k]["driverwait"].until(
                    EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".displayed:last-child .message"), m)
                )
        for k in self.users_dict.keys():
            self.users_dict[k][f"last_{nb_of_new_msg}_messages"] = [
                el.text
                for el in self.users_dict[k]["driver"].find_elements(By.CSS_SELECTOR, ".displayed .message")[
                    -nb_of_new_msg:
                ]
            ]
            self.assertEqual(self.users_dict[k][f"last_{nb_of_new_msg}_messages"], messages)
            self.assertEqual(self.users_dict[k][f"last_{nb_of_new_msg}_messages"], messages)
        long_text = FuzzyText(length=501).fuzz()
        self.users_dict[user1]["message_input"].send_keys(long_text)
        self.users_dict[user1]["submit_btn"].click()
        self.users_dict[user1]["driverwait"].until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".displayed:last-child .message"), long_text[:500])
        )
        self.assertEqual(
            len(self.users_dict[user1]["driver"].find_element(By.CSS_SELECTOR, ".displayed:last-child .message").text),
            500,
        )
        self.users_dict[user1]["message_input"].send_keys(" ")
        self.users_dict[user1]["submit_btn"].click()
        time.sleep(1)
        self.assertFalse(
            self.users_dict[user1]["driver"]
            .find_element(By.CSS_SELECTOR, ".displayed:last-child .message")
            .text.isspace()
        )
