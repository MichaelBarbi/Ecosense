from django.db import models
from user.models import Customer, Staff

class TicketStatus(models.TextChoices):
    OPENED = "Opened", "Opened"
    CLOSED = "Closed", "Closed"

class TicketMessageAuthorType(models.TextChoices):
    Customer = "Customer", "Customer"
    Staff = "Staff", "Staff"

class Ticket(models.Model):

    status = models.CharField(max_length=10, choices=TicketStatus.choices, default=TicketStatus.OPENED)
    subject = models.CharField(max_length=50)
    customer = models.ForeignKey(Customer, related_name="tickets", on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, related_name="tickets", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["subject"]
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        db_table = "ticket"

    def __str__(self):
        return f"{str(self.customer)} - {self.subject}"
    
    @staticmethod
    def getTicketStatusList():
        return TicketStatus.choices

class TicketMessage(models.Model):

    ticket = models.ForeignKey(Ticket, related_name="ticketMessages", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    message = models.TextField(max_length=2000)
    authorType = models.CharField(max_length=10, choices=TicketMessageAuthorType.choices, null=True, blank=True)

    def __str__(self):
        return f"{str(self.ticket)} - {self.pk}"
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Ticket Message"
        verbose_name_plural = "Ticket Messages"
        db_table = "ticket_message"

