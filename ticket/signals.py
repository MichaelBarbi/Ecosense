from django.db.models.signals import post_migrate
from django.dispatch import receiver

from ticket.models import Ticket, TicketMessage, TicketMessageAuthorType, TicketStatus
from user.models import Customer, Staff

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):

    if not Ticket.objects.all():

        # Ticket
        ticket_data = [
            {
                "status": TicketStatus.OPENED,
                "subject": "Errore durante la fase di registrazione di un sensore",
                "customer": 1,
                "staff": None
            },
            {
                "status": TicketStatus.OPENED,
                "subject": "Errore durante la fase di registrazione di un sensore",
                "customer": 2,
                "staff": None
            },
            {
                "status": TicketStatus.CLOSED,
                "subject": "Richiesta aggiunta di un nuovo sensore",
                "customer": 1,
                "staff": 2
            },
        ]

        for td in ticket_data:

            try:

                Ticket.objects.create(
                    status=td["status"],
                    subject=td["subject"],
                    customer=Customer.objects.get(pk=td["customer"]),
                    staff=Staff.objects.get(pk=td["staff"]) if td["staff"] else None
                )
            
            except Exception as e:
                print(str(e))

        # Ticket message
        ticket_message_data = [
            {
                "ticket": 1,
                "message": "Salve\n Volevo chiedervi come mai inserendo il codice del sensore che ho acquistato nell'apposito portale mi da errore.\n\nCordiali saluti\nMichael",
                "authorType": TicketMessageAuthorType.Customer
            },
            {
                "ticket": 2,
                "message": "Salve\n Volevo chiedervi come mai inserendo il codice del sensore che ho acquistato nell'apposito portale mi da errore.\n\nCordiali saluti\nJohn",
                "authorType": TicketMessageAuthorType.Customer
            },
            {
                "ticket": 3,
                "message": "Buongiorno\nVolevi chiedervi se avevate intenzione di inserire un nuovo sensore per il rilevamento di movimenti. Avrei bisogno di un senore di questo tipo e mi piacerebbe acquistarne un altro dei vostri dato che mi sono trovato molto bene con i vostri prodotti.\n\nCordialmente\nMichael",
                "authorType": TicketMessageAuthorType.Customer
            },
            {
                "ticket": 3,
                "message": "Salve Michael\nLa ringraziamo per la vostra fantastica recensione. Le confermo che tra meno di una settimana verranno aggiunti al catalogo un nuovo set di sensori, tra cui un sensore di movimento.\nPer qualsiasi altra richiesta me lo faccia sapere, altrimenti la ringrazio nuovamente e chiudo il ticket.\n\nSaluti\nMichele | Sales Manager.",
                "authorType": TicketMessageAuthorType.Staff
            },
            {
                "ticket": 3,
                "message": "Salve Michele\nGrazie mille per l'esaustiva risposta, non vedo l'ora.\n\nSaluti\nMichael",
                "authorType": TicketMessageAuthorType.Customer
            },
        ]

        for tmd in ticket_message_data:

            try:
                TicketMessage.objects.create(
                    ticket=Ticket.objects.get(pk=tmd["ticket"]),
                    message=tmd["message"],
                    authorType=tmd["authorType"]
                )

            except Exception as e:
                print(str(e))

    