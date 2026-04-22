from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsReceptionistOrAdmin
from apps.visitors.models import Visit
from apps.visitors.serializers import DashboardSummarySerializer


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsReceptionistOrAdmin]
    serializer_class = DashboardSummarySerializer

    def get(self, request):
        today = timezone.localdate()
        visits = Visit.objects.filter(visit_date=today)
        data = {
            'total_today': visits.count(),
            'pending': visits.filter(status=Visit.Status.PENDING).count(),
            'checked_in': visits.filter(status=Visit.Status.CHECKED_IN).count(),
            'checked_out': visits.filter(status=Visit.Status.CHECKED_OUT).count(),
        }
        return Response(DashboardSummarySerializer(data).data)
