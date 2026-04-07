from django import forms
from .models import Complaint, ComplaintUpdate


class ComplaintForm(forms.ModelForm):
    attachments = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False, label='Attach File')

    class Meta:
        model = Complaint
        fields = ['type', 'category', 'title', 'description', 'location', 'incident_date', 'priority', 'is_anonymous']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location in barangay'}),
            'incident_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ComplaintUpdateForm(forms.ModelForm):
    class Meta:
        model = ComplaintUpdate
        fields = ['message', 'new_status']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'new_status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_status'].choices = [('', '-- No status change --')] + list(Complaint.STATUS_CHOICES)
        self.fields['new_status'].required = False