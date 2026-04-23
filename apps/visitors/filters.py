import django_filters

from .models import Visit


class VisitFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='visit_date', lookup_expr='gte', label='From date')
    date_to = django_filters.DateFilter(field_name='visit_date', lookup_expr='lte', label='To date')
    visitor_name = django_filters.CharFilter(field_name='visitor_name', lookup_expr='icontains', label='Visitor')
    host_name = django_filters.CharFilter(field_name='host_name', lookup_expr='icontains', label='Host')
    phone = django_filters.CharFilter(field_name='visitor_phone', lookup_expr='icontains', label='Phone')

    class Meta:
        model = Visit
        fields = ['status', 'visit_date', 'date_from', 'date_to', 'visitor_name', 'host_name', 'phone']
