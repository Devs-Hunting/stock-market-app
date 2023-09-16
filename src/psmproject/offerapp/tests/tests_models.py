import decimal
import shutil
from datetime import date, datetime, timedelta, timezone

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from factories.factories import (
    ComplaintFactory,
    OfferFactory,
    SolutionFactory,
    TaskFactory,
    UserFactory,
)
from offerapp.models import (
    ATTACHMENTS_PATH,
    ComplaintAttachment,
    Offer,
    Solution,
    SolutionAttachment,
)


class TestOfferModel(TestCase):
    """
    Test for Offer Model.
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_user = UserFactory()
        cls.offer = OfferFactory(contractor=cls.test_user)

    def test_should_return_correct_number_for_budget_field(self):
        """
        Test check that budget field is decimal number.
        """

        self.assertIsInstance(self.offer.budget, decimal.Decimal)

    def test_should_raise_exception_when_budget_is_negative(self):
        """
        Test check if is raised an exception when budget is negative.
        """
        offer2 = OfferFactory(contractor=self.test_user)
        offer2.budget = -510.11

        with self.assertRaises(ValidationError):
            offer2.clean()

    def test_should_raise_error_when_budget_is_max_digit_number(self):
        """
        Test check if is raised an exception when budget is over max digit number.
        """
        offer3 = OfferFactory(contractor=self.test_user)
        offer3.budget = 1000000.11

        with self.assertRaises(ValidationError):
            offer3.full_clean()

    def test_should_accept_max_possible_value_for_budget(self):
        """
        Test check that the max possible value for budget is 999999.99.
        """
        self.offer.budget = 999999.99
        self.offer.full_clean()
        self.offer.save()

        self.assertIsInstance(self.offer.budget, decimal.Decimal)

    def test_should_raise_exception_when_there_is_no_contractor_to_offer(self):
        """
        Test check that is raised exception when offer has no contractor.
        """
        with self.assertRaises(Exception):
            Offer.objects.create(description="test offer", realization_time="2022-12-12", budget=1000.0)

    def test_should_delete_offer_when_contractor_is_deleted(self):
        """
        Test check that offer is deleted when contractor is deleted.
        """
        user2 = UserFactory()
        offer_to_delete = OfferFactory(contractor=user2)
        user2.delete()
        self.assertFalse(Offer.objects.filter(id=offer_to_delete.id).exists())

    def test_should_return_default_value_for_accepted_as_false(self):
        """
        Test check that the default value for accepted field is False.
        """

        self.assertEqual(False, self.offer.accepted)

    def test_should_return_default_value_for_paid_as_false(self):
        """
        Test check that the default value for paid field is False.
        """

        self.assertEqual(False, self.offer.paid)

    def test_should_return_default_value_for_created_as_now(self):
        """
        Test check that the default value for created field is now.
        Is comparing string representation of datetime object.
        """

        self.assertEqual(datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"), self.offer.created.strftime("%Y-%m-%d"))

    def test_should_raise_error_when_realization_time_is_in_the_past(self):
        """
        Test checks that is raised error when realization time is in the past.
        """
        offer_in_past = OfferFactory(realization_time=(date.today() - timedelta(days=1)), contractor=self.test_user)

        with self.assertRaises(ValidationError):
            offer_in_past.clean()

    def test_should_raise_validation_error_when_realization_time_is_set_on_today(self):
        """
        Test check that is raised validation error when realization time is set on today.
        """
        offer_today = OfferFactory(realization_time=date.today(), contractor=self.test_user)

        with self.assertRaises(ValidationError):
            offer_today.clean()

    def test_should_create_offer_with_realization_time_in_future(self):
        """
        Test check that offer is created with realization time in future.
        """
        offer_future = OfferFactory(realization_time=(date.today() + timedelta(days=1)), contractor=self.test_user)

        self.assertTrue(Offer.objects.filter(id=offer_future.id).exists())

    def test_should_return_correct_text_as_representation_of_object(self):
        """
        Test check that the representation of object Offer has correct text.
        """
        expected_representation = (
            f"<Offer id={self.offer.id} for Task id={self.offer.task.id}, contractor={self.offer.contractor}>"
        )
        actual_representation = repr(self.offer)

        self.assertEqual(expected_representation, actual_representation)

    def test_should_return_correct_string_representation(self):
        """
        Test check that the string representation of instance of object Offer has correct text.
        """

        expected_string = f"Offer by {self.offer.contractor}"
        actual_string = str(self.offer)

        self.assertEqual(expected_string, actual_string)


class TestComplaintModel(TestCase):
    """
    Test for Complaint Model.
    """

    def setUp(self) -> None:
        """
        Set up data for each individual test.
        """
        super().setUpClass()
        self.test_client = UserFactory()
        self.test_contractor = UserFactory()
        self.test_arbiter = UserFactory()
        self.test_task = TaskFactory(client=self.test_client)
        self.test_offer = OfferFactory(contractor=self.test_contractor, task=self.test_task)
        self.test_complaint = ComplaintFactory(arbiter=self.test_arbiter)
        self.test_solution = SolutionFactory(complaint=self.test_complaint)
        self.test_offer.solution = self.test_solution

    def test_should_set_arbiter_to_null_when_the_arbiter_is_deleted(self):
        """
        Test check that if arbiter is deleted, the field is set to null.
        """
        self.test_arbiter.delete()
        self.test_complaint.refresh_from_db()

        self.assertEqual(None, self.test_complaint.arbiter)

    def test_should_return_default_value_for_closed_as_false(self):
        """
        Test check that the default value for closed is set to False
        """

        self.assertEqual(False, self.test_complaint.closed)

    def test_should_return_default_value_for_created_at_as_now(self):
        """
        Test check that the default value for created_at is now
        """

        self.assertEqual(
            datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M"),
            self.test_complaint.created_at.strftime("%Y-%m-%d %H:%M"),
        )

    def test_should_change_value_for_update_at_as_now_when_object_is_updated(self):
        """
        Test check that after updating the object the value of update_at is now.
        """

        self.test_complaint.content = "New Content"
        update_datetime = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
        self.test_complaint.save()
        self.test_complaint.refresh_from_db()

        self.assertEqual(self.test_complaint.content, "New Content")
        self.assertEqual(update_datetime, self.test_complaint.updated_at.strftime("%Y-%m-%d %H:%M"))

    def test_should_return_correct_text_as_representation_of_object(self):
        """
        Test check that the representation of object Complaint has correct text.
        """
        expected_representation = f"<Complaint id={self.test_complaint.id}, status: {self.test_complaint.closed}>"
        actual_representation = repr(self.test_complaint)

        self.assertEqual(expected_representation, actual_representation)

    def test_should_return_correct_string_representation(self):
        """
        Test check that the string representation of instance of object Complaint has correct text.
        """
        expected_string = (
            f"Complaint id={self.test_complaint.id} for Solution id={self.test_complaint.solution.id}, "
            f"status: {self.test_complaint.closed}."
        )
        actual_string = str(self.test_complaint)

        self.assertEqual(expected_string, actual_string)


class TestSolutionModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_client = UserFactory()
        cls.test_contractor = UserFactory()
        cls.test_arbiter = UserFactory()
        cls.test_task = TaskFactory(client=cls.test_client)
        cls.test_offer = OfferFactory(contractor=cls.test_contractor, task=cls.test_task)
        cls.test_complaint = ComplaintFactory(arbiter=cls.test_arbiter)
        cls.test_solution = SolutionFactory(complaint=cls.test_complaint)
        cls.test_offer.solution = cls.test_solution

    def test_should_return_default_value_for_submitted_as_True(self):

        self.assertEqual(True, self.test_solution.submitted)

    def test_should_return_default_value_for_accepted_as_False(self):

        self.assertEqual(False, self.test_solution.accepted)

    def test_should_return_for_end_attribute_day_as_today(self):
        """
        Test check that date for end is set as date of creation of object.
        """
        self.assertEqual(
            datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"), self.test_solution.end.strftime("%Y-%m-%d")
        )

    def test_should_return_correct_text_as_representation_of_object(self):
        expected_representation = f"<Solution id={self.test_solution.id} - accepted: {self.test_solution.accepted}>"

        self.assertEqual(expected_representation, repr(self.test_solution))

    def test_should_return_correct_string_representation(self):
        expected_string = (
            f"Solution id={self.test_solution.id} for Offer id={self.test_offer.id} "
            f"- accepted: {self.test_solution.accepted}"
        )

        self.assertEqual(expected_string, str(self.test_solution))

    def test_should_set_value_to_null_when_complaint_is_deleted(self):
        self.test_complaint.delete()
        self.test_solution.refresh_from_db()

        self.assertEqual(None, self.test_solution.complaint)


class TestSolutionAttachment(TestCase):
    def setUp(self) -> None:
        super().setUpClass()
        self.test_client = UserFactory()
        self.test_contractor = UserFactory()
        self.test_arbiter = UserFactory()
        self.test_task = TaskFactory(client=self.test_client)
        self.test_offer = OfferFactory(contractor=self.test_contractor, task=self.test_task)
        self.test_solution = Solution.objects.create(description="test solution")
        self.test_offer.solution = self.test_solution
        self.test_attachment = SolutionAttachment.objects.create(
            solution=self.test_solution, attachment=SimpleUploadedFile("test_file.txt", b"content of test file")
        )

    def tearDown(self) -> None:
        file_path = settings.MEDIA_ROOT / ATTACHMENTS_PATH
        shutil.rmtree(file_path, ignore_errors=True)

    def test_should_raise_error_when_max_attachments_number_is_exceeded(self):
        for index in range(SolutionAttachment.MAX_ATTACHMENTS):
            SolutionAttachment.objects.create(
                solution=self.test_solution,
                attachment=SimpleUploadedFile(f"test_file_{index}.txt", b"content of test file"),
            )
        self.excessive_solution_attachment = SolutionAttachment.objects.create(
            solution=self.test_solution,
            attachment=SimpleUploadedFile("test_file_more.txt", b"content of test file"),
        )

        with self.assertRaisesMessage(ValidationError, "You have reached the maximum number of attachments."):
            self.excessive_solution_attachment.clean()

    def test_should_check_and_delete_an_existing_attachment_with_the_same_name(self):
        SolutionAttachment.objects.create(
            solution=self.test_solution,
            attachment=SimpleUploadedFile("test_file.txt", b"content of test file"),
        )
        with self.assertRaises(SolutionAttachment.DoesNotExist):
            SolutionAttachment.objects.get(id=self.test_attachment.id)

        new_attachment_path = f"{ATTACHMENTS_PATH}solutions/{self.test_attachment.solution.id}/test_file.txt"
        new_attachment = SolutionAttachment.objects.get(attachment=new_attachment_path)
        self.assertIsNotNone(new_attachment)

    def test_should_raise_exception_when_not_allowed_file_extension_is_used(self):

        with self.assertRaisesMessage(ValidationError, "File type not allowed"):
            solution_attachment_wrong_extension = SolutionAttachment.objects.create(
                solution=self.test_solution,
                attachment=SimpleUploadedFile("test_file.exe", b"content of test file"),
            )
            solution_attachment_wrong_extension.clean()

    def test_should_get_correct_upload_path_for_attachment_file(self):
        expected_upload_path = f"attachments/solutions/{self.test_attachment.solution.id}/test_file.txt"
        actual_upload_path = str(self.test_attachment.attachment)

        self.assertEqual(expected_upload_path, actual_upload_path)

    def test_should_return_correct_string_representation(self):
        expected_string = (
            f"Solution Attachment: {self.test_attachment.attachment.name} "
            f"for Solution: {self.test_attachment.solution.id}"
        )
        actual_string = str(self.test_attachment)

        self.assertEqual(expected_string, actual_string)

    def test_should_return_correct_text_as_representation_of_object(self):
        expected_representation = (
            f"<Solution Attachment id={self.test_attachment.id}, "
            f"attachment={self.test_attachment.attachment.name}, "
            f"solution_id={self.test_attachment.solution.id}>"
        )
        actual_representation = repr(self.test_attachment)

        self.assertEqual(expected_representation, actual_representation)


class TestComplaintAttachmentModel(TestCase):
    def setUp(self) -> None:
        super().setUpClass()
        self.test_client = UserFactory()
        self.test_contractor = UserFactory()
        self.test_arbiter = UserFactory()
        self.test_task = TaskFactory(client=self.test_client)
        self.test_offer = OfferFactory(contractor=self.test_contractor, task=self.test_task)
        self.test_complaint = ComplaintFactory(arbiter=self.test_arbiter)
        self.test_solution = SolutionFactory(complaint=self.test_complaint)
        self.test_offer.solution = self.test_solution
        self.complaint_attachment = ComplaintAttachment.objects.create(
            complaint=self.test_complaint, attachment=SimpleUploadedFile("test_file.txt", b"content of test file")
        )

    def tearDown(self) -> None:
        file_path = settings.MEDIA_ROOT / ATTACHMENTS_PATH
        shutil.rmtree(file_path, ignore_errors=True)

    def test_should_return_correct_string_representation(self):
        expected_string = (
            f"Complaint Attachment: {self.complaint_attachment.attachment.name}"
            f" for Complaint: {self.complaint_attachment.complaint.id}"
        )
        actual_string = str(self.complaint_attachment)

        self.assertEqual(expected_string, actual_string)

    def test_should_return_correct_text_representation_of_object(self):
        expected_representation = (
            f"<Complaint Attachment id={self.complaint_attachment.id}, "
            f"attachment={self.complaint_attachment.attachment.name}, "
            f"complaint_id={self.complaint_attachment.complaint.id}>"
        )
        actual_representation = repr(self.complaint_attachment)

        self.assertEqual(expected_representation, actual_representation)

    def test_should_get_correct_upload_path_for_attachment_file(self):
        expected_upload_path = f"attachments/complaints/{self.complaint_attachment.complaint.id}/test_file.txt"
        actual_upload_path = str(self.complaint_attachment.attachment)

        self.assertEqual(expected_upload_path, actual_upload_path)

    def test_should_raise_exception_when_not_allowed_file_extension_is_used(self):

        with self.assertRaisesMessage(ValidationError, "File type not allowed"):
            complaint_attachment_wrong_extension = ComplaintAttachment.objects.create(
                complaint=self.test_complaint,
                attachment=SimpleUploadedFile("test_file.exe", b"content of test file"),
            )
            complaint_attachment_wrong_extension.clean()

    def test_should_check_and_delete_an_existing_attachment_with_the_same_name(self):
        ComplaintAttachment.objects.create(
            complaint=self.test_complaint,
            attachment=SimpleUploadedFile("test_file.txt", b"content of test file"),
        )
        with self.assertRaises(ComplaintAttachment.DoesNotExist):
            ComplaintAttachment.objects.get(id=self.complaint_attachment.id)

        new_attachment_path = f"{ATTACHMENTS_PATH}complaints/{self.complaint_attachment.complaint.id}/test_file.txt"
        new_attachment = ComplaintAttachment.objects.get(attachment=new_attachment_path)
        self.assertIsNotNone(new_attachment)

    def test_should_raise_error_when_max_attachments_number_is_exceeded(self):
        for index in range(ComplaintAttachment.MAX_ATTACHMENTS):
            ComplaintAttachment.objects.create(
                complaint=self.test_complaint,
                attachment=SimpleUploadedFile(f"test_file_{index}.txt", b"content of test file"),
            )
        self.excessive_solution_attachment = ComplaintAttachment.objects.create(
            complaint=self.test_complaint,
            attachment=SimpleUploadedFile("test_file_more.txt", b"content of test file"),
        )

        with self.assertRaisesMessage(ValidationError, "You have reached the maximum number of attachments."):
            self.excessive_solution_attachment.clean()
