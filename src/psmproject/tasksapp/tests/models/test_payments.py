from django.test import TestCase
from factories.factories import PaymentFactory
from tasksapp.models import Payment


class TestPaymentModel(TestCase):
    """
    Tests for Payment model
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.new_payment = PaymentFactory(total_amount=1000)

    def test_should_confirm_payment_instance_has_been_created_properly(self):
        """
        Test checks if payment instance has been properly created in DB.
        """
        payments = Payment.objects.all()
        self.assertIn(self.new_payment, payments)

    def test_should_return_correct_value_for_amount_due_to_contractor_field(self):
        """
        Test checks if amount due to contractor value is returned correctly, by default service fee is 15% of total
        amount, then amount due to contractor is 85% of the total cost.
        """
        self.assertEqual(self.new_payment.amount_due_to_contractor, 850)

    def test_should_return_correct_value_for_advance_amount_field(self):
        """
        Test checks if advance amount value is returned correctly, by default advance is 50% of amount due to
        contractor.
        """
        self.assertEqual(self.new_payment.advance_amount, 425)

    def test_should_return_correct_service_fee_amount(self):
        """
        Test checks if service fee amount is returned correctly.
        """
        self.assertEqual(self.new_payment.service_fee, 150)

    def test_should_return_correct_str_representation_when_payment_not_completed(self):
        """
        Test checks if str representation is correct when payment has not been completed yet.
        """
        expected_str = f"Payment: {self.new_payment.total_amount}"
        self.assertEqual(str(self.new_payment), expected_str)

    def test_should_return_correct_str_representation_when_payment_completed(self):
        """
        Test checks if str representation is correct when payment has been completed.
        """
        payment_completed = PaymentFactory(contractor_paid=True)
        expected_str = f"Payment: {payment_completed.total_amount} - COMPLETED"
        self.assertEqual(str(payment_completed), expected_str)
