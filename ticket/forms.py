from django import forms
from .models import Ticket, TicketMessage

class TicketMessageViewForm(forms.ModelForm):

    created_at = forms.DateTimeField(
        label="Created At",
        disabled=True,
        required=False,
        widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S')
    )

    class Meta:
        model = TicketMessage
        exclude = ["ticket"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.disabled = True
            field.required = False
        
        if self.instance and self.instance.pk:
            self.fields['created_at'].initial = self.instance.created_at


class TicketViewForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.disabled = True
            field.required = False

    class Meta:
        model = Ticket
        exclude = []

class TicketAddForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject']

class TicketMessageForm(forms.ModelForm):

    class Meta:
        model = TicketMessage
        fields = ['message']
