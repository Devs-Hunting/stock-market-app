from django.test import TestCase
from factories.factories import OfferFactory, UserFactory


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
        expected_number = 6660.12
        self.offer.budget = 6660.12

        self.assertEqual(expected_number, self.offer.budget)

    def test_should_return_default_value_for_paid_as_false(self):
        """
        Test check that the default value for paid field is False.
        """

        self.assertEqual(False, self.offer.paid)

    def test_should_return_default_value_for_accepted_as_false(self):
        """
        Test check that the default value for accepted field is False.
        """

        self.assertEqual(False, self.offer.accepted)

    def test_should_return_correct_text_as_representation_of_object(self):
        """
        Test check that the representation of object Offer has correct text.
        """
        expected_representation = (
            f"<Offer id={self.offer.id}, contractor={self.offer.contractor}>"
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
