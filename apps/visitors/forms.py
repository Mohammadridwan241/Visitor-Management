from django import forms
from django.utils import timezone

from .models import Visit


class VisitRegistrationForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = [
            'visitor_name',
            'visitor_phone',
            'visitor_email',
            'visitor_company',
            'visitor_id_type',
            'visitor_id_no',
            'purpose_of_visit',
            'visit_date',
            'visit_time',
            'host_name',
            'host_department',
            'host_phone',
            'host_email',
        ]
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'visit_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = ['visitor_name', 'visitor_phone', 'purpose_of_visit', 'visit_date', 'visit_time', 'host_name']
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            field.required = name in required_fields

    def clean_visit_date(self):
        visit_date = self.cleaned_data['visit_date']
        if visit_date < timezone.localdate():
            raise forms.ValidationError('Visit date cannot be in the past.')
        return visit_date
