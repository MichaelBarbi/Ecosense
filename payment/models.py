from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

class CreditCard(models.Model):

    card_number = models.CharField(
        max_length=25,
        validators=[
            RegexValidator(
                regex=r'^[\d\s-]+$',
                message="Card number can only contain digits, spaces, and hyphens."
            )
        ],
        help_text="Digits only. Spaces and dashes are allowed."
    )

    exp_month = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12)
        ]
    )

    exp_year = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ["card_number", "exp_month", "exp_year"]
        verbose_name = "Credit Card"
        verbose_name_plural = "Credit Cards"
        db_table = "credit_card"

