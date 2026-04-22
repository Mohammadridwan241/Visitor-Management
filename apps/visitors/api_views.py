from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsReceptionistOrAdmin

from .filters import VisitFilter
from .models import Visit
from .serializers import (
    VisitCheckInSerializer,
    VisitCheckOutSerializer,
    VisitDetailSerializer,
    VisitListSerializer,
    VisitRegistrationSerializer,
)


class VisitRegistrationAPIView(generics.CreateAPIView):
    serializer_class = VisitRegistrationSerializer
    permission_classes = [AllowAny]


class VisitListAPIView(generics.ListAPIView):
    queryset = Visit.objects.all()
    serializer_class = VisitListSerializer
    permission_classes = [IsReceptionistOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VisitFilter
    search_fields = ['visitor_name', 'visitor_phone', 'reference_no', 'host_name']
    ordering_fields = ['visit_date', 'created_at', 'status']


class VisitDetailAPIView(generics.RetrieveAPIView):
    queryset = Visit.objects.select_related('checked_in_by', 'checked_out_by')
    serializer_class = VisitDetailSerializer
    permission_classes = [IsReceptionistOrAdmin]


class VisitByReferenceAPIView(generics.RetrieveAPIView):
    serializer_class = VisitDetailSerializer
    permission_classes = [IsReceptionistOrAdmin]
    lookup_url_kwarg = 'reference_no'

    def get_object(self):
        return get_object_or_404(Visit, reference_no=self.kwargs['reference_no'])


class VisitByTokenAPIView(generics.RetrieveAPIView):
    serializer_class = VisitDetailSerializer
    permission_classes = [IsReceptionistOrAdmin]
    lookup_url_kwarg = 'token'

    def get_object(self):
        return get_object_or_404(Visit, qr_token=self.kwargs['token'])


class VisitCheckInAPIView(APIView):
    permission_classes = [IsReceptionistOrAdmin]
    serializer_class = VisitCheckInSerializer

    def post(self, request, pk):
        serializer = VisitCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        visit = get_object_or_404(Visit, pk=pk)
        try:
            visit.perform_check_in(request.user)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(VisitDetailSerializer(visit, context={'request': request}).data, status=status.HTTP_200_OK)


class VisitCheckOutAPIView(APIView):
    permission_classes = [IsReceptionistOrAdmin]
    serializer_class = VisitCheckOutSerializer

    def post(self, request, pk):
        serializer = VisitCheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        visit = get_object_or_404(Visit, pk=pk)
        try:
            visit.perform_check_out(request.user)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc
        return Response(VisitDetailSerializer(visit, context={'request': request}).data, status=status.HTTP_200_OK)
