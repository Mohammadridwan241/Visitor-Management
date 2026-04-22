from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import DetailView

from .forms import VisitRegistrationForm
from .models import Visit
from .services import create_visit


def register_visit(request):
    if request.method == 'POST':
        form = VisitRegistrationForm(request.POST)
        if form.is_valid():
            visit = create_visit(form.cleaned_data)
            messages.success(request, 'Registration submitted successfully.')
            return redirect('visitors:registration-success', reference_no=visit.reference_no)
    else:
        form = VisitRegistrationForm()
    return render(request, 'visitors/register.html', {'form': form})


class RegistrationSuccessView(DetailView):
    model = Visit
    template_name = 'visitors/success.html'
    context_object_name = 'visit'
    slug_field = 'reference_no'
    slug_url_kwarg = 'reference_no'
