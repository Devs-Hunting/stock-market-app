from django.test import TestCase
from factories.factories import PaymentFactory
from tasksapp.models import Payment


class TestPaymentModel(TestCase):
    """
    Tests for Payment model
    """

    def setUp(self) -> None:
        super().setUpClass()
        self.payment = PaymentFactory(total_cost=1000)

    def test_should_confirm_payment_instance_has_been_created_properly(self):
        """
        Test checks if payment has been properly created in DB.
        """
        payments = Payment.objects.all()
        self.assertIn(self.payment, payments)

    def test_should_return_correct_value_for_amount_due_to_contractor_field(self):
        """
        Test checks if amount due to contractor value is returned correctly, by default service fee is 15% of total
        amount, then amount due to contractor is 85% of the total cost.
        """
        self.assertEqual(self.payment.amount_due_to_contractor, 850)

    def test_should_return_correct_value_for_advance_amount_field(self):
        """
        Test checks if advance amount value is returned correctly, by default advance is 20% of amount due to
        contractor.
        """
        self.assertEqual(self.payment.advance_amount, 170)

    def test_should_return_correct_service_fee_amount(self):
        """
        Test checks if service fee amount is returned correctly.
        """
        self.assertEqual(self.payment.service_fee, 150)

    def test_should_return_correct_boolean_value_from_advance_paid_property_when_advance_not_paid_yet(self):
        """
        Test checks if advance_paid property boolean value is false when advance has not been paid yet.
        """
        self.assertFalse(self.payment.advance_paid)

    def test_should_return_correct_boolean_value_from_completed_property_when_payment_not_completed_yet(self):
        """
        Test checks if completed property boolean value is false when payment has not been completed yet.
        """
        self.assertFalse(self.payment.completed)

    def test_should_return_correct_boolean_value_from_advance_paid_property_when_advance_paid(self):
        """
        Test checks if advance_paid property boolean value is true when advance has been paid.
        """
        self.payment.amount_paid = self.payment.advance_amount
        self.payment.save(update_fields=["amount_paid"])
        self.assertTrue(self.payment.advance_paid)

    def test_should_return_correct_boolean_value_from_completed_property_payment_completed(self):
        """
        Test checks if completed property boolean value is true when payment has been completed.
        """
        self.payment.amount_paid = self.payment.total_cost
        self.payment.save(update_fields=["total_cost"])
        self.assertTrue(self.payment.completed)

    def test_should_return_correct_str_representation_when_payment_not_completed(self):
        """
        Test checks if str representation is correct when payment has not been completed yet.
        """
        expected_str = f"Payment: {self.payment.total_cost}"
        self.assertEqual(str(self.payment), expected_str)

    def test_should_return_correct_str_representation_when_payment_completed(self):
        """
        Test checks if str representation is correct when payment has been completed.
        """
        self.payment.amount_paid = self.payment.total_cost
        self.payment.save(update_fields=["total_cost"])
        expected_str = f"Payment: {self.payment.total_cost} - COMPLETED"
        self.assertEqual(str(self.payment), expected_str)
