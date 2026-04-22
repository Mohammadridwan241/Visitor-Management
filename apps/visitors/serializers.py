from django.utils import timezone
from rest_framework import serializers

from .models import Visit
from .services import create_visit


class VisitRegistrationSerializer(serializers.ModelSerializer):
    qr_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Visit
        fields = [
            'id',
            'reference_no',
            'visitor_name',
            'visitor_phone',
            'visitor_email',
            'visitor_company',
            'visitor_id_type',
            'visitor_id_no',
            'purpose_of_visit',
            'host_name',
            'host_department',
            'host_phone',
            'host_email',
            'visit_date',
            'visit_time',
            'qr_token',
            'qr_image_url',
            'status',
            'submitted_at',
        ]
        read_only_fields = ['id', 'reference_no', 'qr_token', 'qr_image_url', 'status', 'submitted_at']

    def validate_visit_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError('Visit date cannot be in the past.')
        return value

    def create(self, validated_data):
        return create_visit(validated_data)

    def get_qr_image_url(self, obj) -> str | None:
        request = self.context.get('request')
        if not obj.qr_code_image:
            return None
        url = obj.qr_code_image.url
        return request.build_absolute_uri(url) if request else url


class VisitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = [
            'id',
            'reference_no',
            'visitor_name',
            'visitor_phone',
            'host_name',
            'visit_date',
            'visit_time',
            'status',
            'checked_in_at',
            'checked_out_at',
        ]


class VisitDetailSerializer(serializers.ModelSerializer):
    can_check_in = serializers.BooleanField(read_only=True)
    can_check_out = serializers.BooleanField(read_only=True)
    qr_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = '__all__'

    def get_qr_image_url(self, obj) -> str | None:
        request = self.context.get('request')
        if not obj.qr_code_image:
            return None
        url = obj.qr_code_image.url
        return request.build_absolute_uri(url) if request else url


class VisitCheckInSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True)


class VisitCheckOutSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True)


class DashboardSummarySerializer(serializers.Serializer):
    total_today = serializers.IntegerField()
    pending = serializers.IntegerField()
    checked_in = serializers.IntegerField()
    checked_out = serializers.IntegerField()
