from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from user.views import customer_login_required, sales_login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from .forms import *
import json

@login_required
def TicketMessagesView(request, pk):

    if request.method == "GET":

        try:

            # Get the ticket
            ticket = get_object_or_404(Ticket, pk=pk)
            if not ticket:
                raise ValueError("The ticket does not exist")
            
            canAnswer = False


            if hasattr(request.user, "customer"):
                # Verify that the customer is the same as the ticket customer
                if request.user.customer == ticket.customer:
                    canAnswer = True

            if hasattr(request.user, "staff"):
                # Can answer only if no staff is already associated withe the ticket and,
                # in case the attribute staff is not null, then the current staff member must be the same
                if not ticket.staff or ticket.staff == request.user.staff:
                    canAnswer = True

            if ticket.status == TicketStatus.CLOSED:
                canAnswer = False
                
            # Get the ticket form
            ticketViewForm = TicketViewForm(instance=ticket)

            # Collect forms for every message
            ticketMessagesForms = []

            ticketMessages = TicketMessage.objects.filter(ticket=ticket).order_by("created_at")
            for ticketMessage in ticketMessages.all():
                ticketMessagesForms.append(TicketMessageViewForm(instance=ticketMessage))

            # Get the new TicketMessage Form
            newTicketMessageForm = TicketMessageForm()

            return render(request, template_name="ticket/ticket.html", context={
                "title": f"Ticket {ticket.pk}",
                "ticketViewForm": ticketViewForm,
                "ticketMessagesForms": ticketMessagesForms,
                "ticket": ticket,
                "newTicketMessageForm": newTicketMessageForm,
                "canAnswer": canAnswer
            })

        except Exception as e:
            messages.error(request, f"An error occured while viewing the ticket: {str(e)}")
            return redirect("ticket:tickets")
        
    elif request.method == "POST":

        try:
            
            # Get the Ticket message form with data
            ticketMessageForm = TicketMessageForm(request.POST)
            if not ticketMessageForm.is_valid():
                raise ValueError("The form is not valid")
            
            ticket = get_object_or_404(Ticket, pk=pk)

            if hasattr(request.user, "customer"):
                if request.user.customer != ticket.customer:
                    raise ValueError("The customer of the ticket is not the same as of the current")
                
            if hasattr(request.user, "staff"):
                if ticket.staff and ticket.staff != request.user.staff:
                    raise ValueError("The staff of the ticket is not the same as of the current")

            ticketMessage = ticketMessageForm.save(commit=False)
            ticketMessage.ticket = ticket
            ticketMessage.authorType = TicketMessageAuthorType.Staff if hasattr(request.user, "staff") else TicketMessageAuthorType.Customer

            ticketMessage.save()

            # Update ticket staff member
            if hasattr(request.user, "staff") and not ticket.staff:
                ticket.staff = request.user.staff
                ticket.save()

            messages.success(request, f"The message has been correctly sent")
            return redirect("ticket:tickets_view", pk)

        except Exception as e:
            messages.error(request, f"The new message has not been sent: {str(e)}")
            return redirect("ticket:tickets_view", pk)

@sales_login_required
@require_POST
def orderStatusUpdate(request, pk):

    try:

        ticket = get_object_or_404(Ticket, pk=pk)
        if not ticket:
            raise ValueError("The order doesn't exist")
        
        # Get the status
        data = json.loads(request.body)
        new_status = data.get("status")
        if not new_status:
            raise ValueError("The status is invalid")
        
        ticket.status = new_status

        ticket.save()

        messages.success(request, f"The status for ticket n. {ticket.pk} has been successfully updated")
        return JsonResponse({"success": True})

    except Exception as e:
        messages.error(request, f"An error occured while updating the status: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

# Create a ticket
@customer_login_required
def ticketCreateView(request):

    if request.method == "GET":

        try: 
        
            # Get the Ticket form
            ticketForm = TicketAddForm()

            # Get the TicketMessage Form
            ticketMessageForm = TicketMessageForm()

            return render(request, template_name="ticket/addTicket.html", context={
                "title": "Add Ticket",
                "ticketForm": ticketForm,
                "ticketMessageForm": ticketMessageForm
            })

        except Exception as e:
            messages.error(request, f"Ticket creation is currently unavailable: {str(e)}")
            return redirect("ticket:tickets")
    
    elif request.method == "POST":

        try:
            
            ticketAddForm = TicketAddForm(request.POST)
            ticketMessageForm = TicketMessageForm(request.POST)

            if not ticketAddForm.is_valid() or not ticketMessageForm.is_valid():
                raise ValueError("The form is invalid")
            
            ticket = ticketAddForm.save(commit=False)
            ticket.customer = request.user.customer
            ticket.save()

            ticketMessage = ticketMessageForm.save(commit=False)
            ticketMessage.ticket = ticket
            ticketMessage.authorType = TicketMessageAuthorType.Customer
            ticketMessage.save()

            messages.success(request, f"The ticket has been created")
            return redirect("ticket:tickets")

        except Exception as e:
            messages.error(request, f"The ticket has not been created: {str(e)}")
            return redirect("ticket:tickets_add")

# Ticket List View
@method_decorator(login_required, name="dispatch")
class TicketListView(ListView):

    model = Ticket
    template_name = "ticket/tickets.html"
    success_url = reverse_lazy("tickets")
    context_object_name = "tickets"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Tickets"

        if hasattr(self.request.user, "staff"):
            context["tickets_statuses"] = Ticket.getTicketStatusList()

        return context
    
    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'customer'):
            return Ticket.objects.filter(customer=user.customer).order_by('-id')
        elif hasattr(user, 'staff'):
            return Ticket.objects.all().order_by('-id')
        else:
            return Ticket.objects.none()
