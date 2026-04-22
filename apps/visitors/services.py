from django.db import transaction

from .models import AuditLog, Visit


@transaction.atomic
def create_visit(validated_data):
    visit = Visit(
        **validated_data,
        reference_no=Visit.generate_reference_no(),
        qr_token=Visit.generate_qr_token(),
    )
    visit.full_clean()
    visit.save()
    visit.generate_qr_code(save=True)
    AuditLog.objects.create(visit=visit, action=AuditLog.Action.SUBMITTED, note='Visitor submitted registration.')
    return visit
