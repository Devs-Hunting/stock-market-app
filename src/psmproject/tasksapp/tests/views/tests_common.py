import os
import shutil

from django.test import Client, TestCase
from django.urls import reverse
from factories.factories import (
    ComplaintFactory,
    OfferFactory,
    TaskAttachmentFactory,
    TaskFactory,
    UserFactory,
)
from tasksapp.models import ATTACHMENTS_PATH, Complaint, Task


class TestCommonTaskDetailView(TestCase):
    """
    Test case for the Task Detail View
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase
        """
        super().setUpTestData()
        cls.user = UserFactory()
        cls.test_task1 = TaskFactory(client=cls.user)
        cls.test_task2 = TaskFactory(client=cls.user)
        cls.test_attachment1 = TaskAttachmentFactory(task=cls.test_task1)
        cls.test_attachment2 = TaskAttachmentFactory(task=cls.test_task2)

    def tearDown(self) -> None:
        file_path = os.path.join(ATTACHMENTS_PATH)
        shutil.rmtree(file_path, ignore_errors=True)
        super().tearDown()

    def test_should_retrieve_task_detail_with_valid_task_id(self):
        """
        Test case to check if Task Detail View works correctly with a valid task id
        """
        self.client.login(username=self.user.username, password="secret")
        response = self.client.get(reverse("task-detail", kwargs={"pk": self.test_task1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasksapp/task_detail.html")
        self.assertIn("attachments", response.context)
        self.assertIn("task", response.context)
        self.assertEqual(response.context["task"], self.test_task1)

    def test_should_require_login_for_task_detail_access(self):
        """
        Test case to check if Task Detail View requires user login
        """
        self.client.logout()
        response = self.client.get(reverse("task-detail", kwargs={"pk": self.test_task1.id}))
        self.assertRedirects(response, f"/users/accounts/login/?next=/tasks/{self.test_task1.id}")


class TaskDeleteViewTest(TestCase):
    """
    Test case for the Task Delete View
    """

    def setUp(self):
        """
        Set up data for each individual test
        """
        super().setUp()
        self.client = Client()
        self.user = UserFactory.create()
        self.task = TaskFactory.create(client=self.user)
        self.client.force_login(self.user)

    def tearDown(self) -> None:
        file_path = os.path.join(ATTACHMENTS_PATH)
        shutil.rmtree(file_path, ignore_errors=True)
        super().tearDown()

    def test_should_block_unauthorized_task_delete_access(self):
        """
        Test case to check if unauthorized task deletion is blocked
        """
        other_task = TaskFactory.create()

        response = self.client.get(reverse("task-delete", args=[other_task.id]))
        self.assertEqual(response.status_code, 302)

    def test_should_delete_task_with_allowed_statuses(self):
        """
        Test case to check if tasks with allowed statuses are deleted
        """
        for status in [Task.TaskStatus.OPEN, Task.TaskStatus.ON_HOLD]:
            self.task.status = status
            self.task.save()

            task_from_db = Task.objects.get(id=self.task.id)
            self.assertEqual(task_from_db.status, status)

            response = self.client.post(reverse("task-delete", args=[self.task.id]))
            self.assertEqual(response.status_code, 302)
            self.assertFalse(Task.objects.filter(id=self.task.id).exists())

            # Recreate the task for the next loop iteration
            self.task = TaskFactory.create(client=self.user)

    def test_should_not_delete_task_with_disallowed_statuses(self):
        """
        Test case to check if tasks with disallowed statuses are not deleted
        """
        for status in [
            Task.TaskStatus.ON_GOING,
            Task.TaskStatus.OBJECTIONS,
            Task.TaskStatus.COMPLETED,
            Task.TaskStatus.CANCELLED,
        ]:
            self.task.status = status
            self.task.save()

            task_from_db = Task.objects.get(id=self.task.id)
            self.assertEqual(task_from_db.status, status)

            response = self.client.post(reverse("task-delete", args=[self.task.id]))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(Task.objects.filter(id=self.task.id).exists())

    def test_should_allow_creator_to_delete_task(self):
        """
        Test case to check if task creator can delete the task
        """
        response = self.client.post(reverse("task-delete", args=[self.task.id]))
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=self.task.id)

    def test_should_handle_attempt_to_delete_nonexistent_task(self):
        """
        Test case to check if attempting to delete a non-existent task is handled correctly
        """
        temp_task = TaskFactory.create(client=self.user)
        temp_task_id = temp_task.id
        temp_task.delete()

        response = self.client.post(reverse("task-delete", args=[temp_task_id]))
        self.assertEqual(response.status_code, 404)


class TestComplaintCreateView(TestCase):
    """
    Test Case for Complaint Create View.
    """

    def setUp(self) -> None:
        """
        Set up data for each test case.
        """
        super().setUp()
        self.client = Client()
        self.user = UserFactory.create()
        self.task = TaskFactory.create(client=self.user, status=Task.TaskStatus.ON_GOING)
        self.offer = OfferFactory.create(task=self.task)
        self.task.selected_offer = self.offer
        self.task.save()
        self.client.force_login(self.user)
        self.data = {"complainant": self.user, "task": self.task, "content": "Complaint content"}
        self.url = reverse("complaint-create", kwargs={"task_pk": self.task.id})

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Task.objects.all().delete()
        Complaint.objects.all().delete()
        super().tearDown()

    def test_should_create_complaint_object_and_redirect_to_proper_page(self):
        """
        Test verify that a complaint object is created and the user is redirected to the proper page.
        """

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Complaint.objects.filter(task=self.task).count(), 1)

    def test_should_redirect_to_proper_url_after_success(self):
        """
        Test verify that a complaint object is created and the user is redirected to the proper page.
        """
        response = self.client.post(self.url, self.data, follow=True)
        complaint = Complaint.objects.filter(task=self.task).first()

        self.assertRedirects(
            response,
            reverse("complaint-detail", kwargs={"pk": complaint.id}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_should_redirect_when_user_is_not_logged_in(self):
        """
        Test checks that user is redirected to login page when user is not logged in.
        """
        self.client.logout()

        response = self.client.post(self.url, self.data, follow=True)

        self.assertRedirects(
            response,
            f"/users/accounts/login/?next=/tasks/complaint/add/task/{self.task.id}",
        )

    def test_should_redirect_when_task_dont_exist(self):
        """
        Test checks that user is redirected to task list page when task does not exist.
        """

        response = self.client.post(reverse("complaint-create", kwargs={"task_pk": 2}), self.data, follow=True)

        self.assertRedirects(
            response,
            reverse("tasks-client-list"),
        )

    def test_should__block_add_complaint_when_task_status_is_cancelled(self):
        """
        Test verify that user is redirected to task detail page when task status is cancelled.
        """
        self.task.status = Task.TaskStatus.CANCELLED
        self.task.save()

        response = self.client.post(self.url, self.data, follow=True)

        self.assertRedirects(
            response,
            reverse("task-detail", kwargs={"pk": self.task.id}),
        )

    def test_should_check_that_task_is_in_context(self):
        """
        Test checks that the task is in the context.
        """

        response = self.client.get(self.url)
        task = response.context.get("task")
        self.assertIsNotNone(task)

    def test_should_check_that_created_complaint_assigned_user_as_complainant(self):
        """
        Test verify that a complaint object has the user assigned as complainant.
        """
        self.client.post(self.url, self.data, follow=True)

        self.assertEqual(Complaint.objects.filter(task=self.task).first().complainant, self.user)

    def test_should_check_that_task_has_status_objections_after_creating_complaint(self):
        """
        Test checks that the task has status objections after creating complaint.
        """
        self.client.post(self.url, self.data, follow=True)

        self.assertEqual(Complaint.objects.filter(task=self.task).first().task.status, Task.TaskStatus.OBJECTIONS)

    def test_should_check_that_complaint_can_be_create_by_contractor(self):
        """
        Test check that complaint can be created by contractor.
        """
        self.task_contractor = UserFactory.create()
        offer = OfferFactory.create(task=self.task, contractor=self.task_contractor)
        self.task.selected_offer = offer
        self.task.save()
        self.client.logout()
        self.client.force_login(self.task_contractor)
        self.client.post(self.url, self.data, follow=True)

        self.task.refresh_from_db()
        self.assertEqual(Complaint.objects.filter(task=self.task).count(), 1)
        self.assertEqual(Complaint.objects.filter(task=self.task).first().task.status, Task.TaskStatus.OBJECTIONS)
        self.assertEqual(Complaint.objects.filter(task=self.task).first().complainant, self.task_contractor)


class TestComplaintEditView(TestCase):
    """
    Test Case for Complaint Edit View.
    """

    def setUp(self) -> None:
        """
        Setting up method that is run before every individual test.
        """
        super().setUp()
        self.user = UserFactory.create()
        self.task = TaskFactory.create(client=self.user)
        self.complaint = ComplaintFactory.create(task=self.task, complainant=self.user)
        self.client.force_login(self.user)
        self.url = reverse("complaint-edit", kwargs={"pk": self.task.id})

        self.data = {"content": "New edited content"}

    def tearDown(self) -> None:
        """
        Method delete Task and Complaint objects after every individual test.
        """
        Task.objects.all().delete()
        Complaint.objects.all().delete()
        super().tearDown()

    def test_should_return_status_code_200_when_request_is_sent(self):
        """
        Test check that status code is 200 when request is sent.
        """
        response = self.client.post(self.url, self.data, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_should_update_complaint_object(self):
        """
        Test verify that complaint object is updated and user is redirected to proper page.
        """
        response = self.client.post(self.url, self.data, follow=True)

        self.assertRedirects(response, reverse("complaint-detail", kwargs={"pk": self.complaint.id}))
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.content, self.data["content"])

    def test_should_return_non_context_when_no_user_is_log_in(self):
        """
        Test check that user is redirected to login page when user is not logged in.
        """
        self.client.logout()

        response = self.client.post(self.url, self.data, follow=True)

        self.assertRedirects(
            response,
            f"/users/accounts/login/?next=/tasks/complaint/{self.complaint.id}/edit",
        )

    def test_should_redirect_if_user_is_not_complainant(self):
        """
        Test check that user is redirected to complaint detail page when user is not complainant.
        """
        new_user = UserFactory.create()
        self.client.logout()
        self.client.force_login(new_user)
        response = self.client.post(self.url, self.data, follow=True)

        self.assertRedirects(
            response,
            reverse("complaint-detail", kwargs={"pk": self.complaint.id}),
        )

    def test_should_check_that_task_is_in_context(self):
        """
        Test checks that task object is in the context.
        """
        response = self.client.get(self.url)
        task = response.context.get("task")
        self.assertIsNotNone(task)


class TestComplaintDetailView(TestCase):
    """
    Test Case for the Complaint Detail View.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up data for the whole TestCase
        """
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.task = TaskFactory.create(client=cls.user)
        cls.complaint = ComplaintFactory.create(task=cls.task, complainant=cls.user)
        cls.url = reverse("complaint-detail", kwargs={"pk": cls.complaint.id})

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Delete objects after whole Test Case.
        """
        Task.objects.all().delete()
        Complaint.objects.all().delete()
        super().tearDownClass()

    def setUp(self) -> None:
        """
        Set up data for each individual test.
        """
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    def test_should_return_complaint_detail_for_valid_complaint_id(self):
        """
        Test checks that complaint detail is returned for valid complaint id.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/complaint_detail.html")
        self.assertEqual(self.response.context["object"], self.complaint)
        self.assertEqual(self.response.context["is_complainant"], True)

    def test_should_redirect_when_user_is_not_log_in(self):
        """
        Test checks that user is redirected to login page when user is not logged in.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"/users/accounts/login/?next=/tasks/complaint/{self.complaint.id}",
        )


class TestComplaintDeleteView(TestCase):
    """
    Test Case for the Complaint Delete View.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up data for the whole TestCase.
        """
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.task = TaskFactory.create(client=cls.user)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Delete objects after whole Test Case.
        """
        Task.objects.all().delete()
        super().tearDownClass()

    def setUp(self) -> None:
        """
        Set up data for each individual test.
        """
        super().setUp()
        self.complaint = ComplaintFactory.create(task=self.task, complainant=self.user)
        self.url = reverse("complaint-delete", kwargs={"pk": self.complaint.id})
        self.client.login(username=self.user.username, password="secret")

    def tearDown(self) -> None:
        """
        Delete all complaint objects after each individual test.
        """
        Complaint.objects.all().delete()
        super().tearDown()

    def test_should_allow_delete_complaint_by_complainant(self):
        """
        Test checks that complaint can be deleted by complainant.
        """
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)

        with self.assertRaises(Complaint.DoesNotExist):
            Complaint.objects.get(id=self.complaint.id)

    def test_should_redirect_when_user_is_not_complainant(self):
        """
        Test verify that user is redirected when he try delete complaint and user is not complainant.
        """
        new_user = UserFactory.create()
        self.client.logout()
        self.client.force_login(new_user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("task-detail", kwargs={"pk": self.task.id}),
        )

    def test_should_redirect_when_user_want_delete_closed_complaint(self):
        """
        Test checks that user is redirected when he try delete complaint with attribute closed - True.
        """
        self.complaint.closed = True
        self.complaint.save()
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("task-detail", kwargs={"pk": self.task.id}),
        )

    def test_should_redirect_when_user_is_not_log_in(self):
        """
        Test checks that user is redirected to login page when user is not logged in.
        """
        self.client.logout()
        response = self.client.post(self.url, follow=True)

        self.assertRedirects(
            response,
            f"/users/accounts/login/?next=/tasks/complaint/{self.task.id}/delete",
        )

    def test_should_after_delete_change_task_status_to_on_going(self):
        """
        Test verifies that task status is changed to on going after deleting complaint.
        """
        self.client.post(self.url)
        self.task.refresh_from_db()

        self.assertEqual(self.task.status, Task.TaskStatus.ON_GOING)
