import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.visitors.filters import VisitFilter
from apps.visitors.models import Visit


def receptionist_required(user):
    return user.is_authenticated and (getattr(user, 'is_receptionist', False) or getattr(user, 'is_admin', False))


def protected(view_func):
    return login_required(user_passes_test(receptionist_required)(view_func))


@protected
def dashboard(request):
    today = timezone.localdate()
    visits_today = Visit.objects.filter(visit_date=today)
    context = {
        'total_today': visits_today.count(),
        'pending': visits_today.filter(status=Visit.Status.PENDING).count(),
        'checked_in': visits_today.filter(status=Visit.Status.CHECKED_IN).count(),
        'checked_out': visits_today.filter(status=Visit.Status.CHECKED_OUT).count(),
        'recent_visits': Visit.objects.all()[:10],
    }
    return render(request, 'reception/dashboard.html', context)


@protected
def visit_list(request):
    filtered = VisitFilter(request.GET, queryset=Visit.objects.all())
    return render(request, 'reception/visit_list.html', {'filter': filtered, 'visits': filtered.qs[:200]})


@protected
def scan(request):
    token = request.GET.get('token')
    visit = None
    if token:
        visit = Visit.objects.filter(qr_token=token).first()
        if not visit:
            messages.error(request, 'Invalid or tampered QR token.')
    return render(request, 'reception/scan.html', {'visit': visit, 'token': token})


@protected
def scan_token(request, token):
    visit = get_object_or_404(Visit, qr_token=token)
    return render(request, 'reception/visit_detail.html', {'visit': visit})


@protected
def visit_detail(request, pk):
    visit = get_object_or_404(Visit, pk=pk)
    return render(request, 'reception/visit_detail.html', {'visit': visit})


@protected
def check_in(request, pk):
    visit = get_object_or_404(Visit, pk=pk)
    if request.method == 'POST':
        try:
            visit.perform_check_in(request.user)
            messages.success(request, 'Visitor checked in successfully.')
        except ValidationError as exc:
            messages.error(request, '; '.join(exc.messages))
    return redirect('reception:visit-detail', pk=visit.pk)


@protected
def check_out(request, pk):
    visit = get_object_or_404(Visit, pk=pk)
    if request.method == 'POST':
        try:
            visit.perform_check_out(request.user)
            messages.success(request, 'Visitor checked out successfully.')
        except ValidationError as exc:
            messages.error(request, '; '.join(exc.messages))
    return redirect('reception:visit-detail', pk=visit.pk)


@protected
def reports(request):
    filtered = VisitFilter(request.GET, queryset=Visit.objects.all())
    summary = filtered.qs.values('status').annotate(total=Count('id')).order_by('status')
    return render(request, 'reception/reports.html', {'filter': filtered, 'summary': summary, 'visits': filtered.qs[:200]})


@protected
def export_csv(request):
    filtered = VisitFilter(request.GET, queryset=Visit.objects.all())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="visitor-report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Reference', 'Visitor', 'Phone', 'Host', 'Date', 'Time', 'Status', 'Checked in', 'Checked out'])
    for visit in filtered.qs:
        writer.writerow([
            visit.reference_no,
            visit.visitor_name,
            visit.visitor_phone,
            visit.host_name,
            visit.visit_date,
            visit.visit_time,
            visit.status,
            visit.checked_in_at,
            visit.checked_out_at,
        ])
    return response
