from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator

class CreditCard(models.Model):
    card_number = models.CharField(
        max_length=19,  # 16 numbers + eventually spaces
        validators=[
            RegexValidator(r'^\d{13,19}$', message="The card number must contain only digits (13-19).")
        ],
        help_text="Only numbers, no spaces.",
    )

    cvc = models.CharField(
        max_length=4,
        validators=[
            RegexValidator(r'^\d{3,4}$', message="CVC must contain 3 or 4 numbers.")
        ],
        help_text="3 or 4 numbers, depending on the circuit.",
    )

    exp_month = models.PositiveSmallIntegerField(
        validators=[
            MinLengthValidator(1),
            MaxLengthValidator(12)
        ],
    )

    exp_year = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ["card_number", "cvc", "exp_month", "exp_year"]
        verbose_name = "Credit Card"
        verbose_name_plural = "Credit Cards"
        db_table = "credit_card"

