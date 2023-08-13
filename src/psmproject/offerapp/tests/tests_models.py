import decimal
from datetime import date, datetime, timedelta, timezone

from django.core.exceptions import ValidationError
from django.test import TestCase
from factories.factories import OfferFactory, UserFactory
from offerapp.models import Offer


class TestOfferModel(TestCase):
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
            offer_no_contractor = Offer.objects.create(
                description="test offer", realization_time="2022-12-12", budget=1000.0
            )

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

        self.assertEqual(
            datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M"), self.offer.created.strftime("%Y-%m-%d %H:%M")
        )

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
