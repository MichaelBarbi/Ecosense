from django.db import models
from user.models import Customer

# Group of sensor
class Group(models.Model):

    name = models.CharField(max_length=70)
    description = models.TextField(max_length=200, null=True, blank=True)
    customer = models.ForeignKey(Customer, related_name="groups", on_delete=models.CASCADE)
    group_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Group"
        verbose_name_plural = "Groups"
        db_table = "db_group"
        constraints = [
            models.UniqueConstraint(fields=["customer", "group_id"], name="unique_group_id_per_customer"),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.group_id is None:  # only set if not already defined

            last_group = Group.objects.filter(customer=self.customer).exclude(group_id__isnull=True).order_by('-group_id').first()
            self.group_id = 1 if not last_group else last_group.group_id + 1

        super().save(*args, **kwargs)
