from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import NormalizedRecord
from .serializers import NormalizedRecordSerializer, RecordReviewSerializer


class NormalizedRecordViewSet(viewsets.ModelViewSet):
    queryset = NormalizedRecord.objects.all()
    serializer_class = NormalizedRecordSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant_id = self.request.query_params.get('tenant')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(review_status=status_filter)

        scope_filter = self.request.query_params.get('scope')
        if scope_filter:
            queryset = queryset.filter(scope=scope_filter)

        activity_filter = self.request.query_params.get('activity_type')
        if activity_filter:
            queryset = queryset.filter(activity_type=activity_filter)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(facility_name__icontains=search) |
                Q(facility_code__icontains=search) |
                Q(description__icontains=search) |
                Q(source_reference__icontains=search)
            )

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def summary(self, request):
        tenant_id = request.query_params.get('tenant')
        if not tenant_id:
            return Response({'error': 'tenant parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        records = NormalizedRecord.objects.filter(tenant_id=tenant_id)

        summary = {
            'total': records.count(),
            'pending': records.filter(review_status='PENDING').count(),
            'approved': records.filter(review_status='APPROVED').count(),
            'rejected': records.filter(review_status='REJECTED').count(),
            'suspicious': records.filter(suspicious_flag=True).count(),
            'by_scope': {
                'scope1': records.filter(scope='SCOPE1').count(),
                'scope2': records.filter(scope='SCOPE2').count(),
                'scope3': records.filter(scope='SCOPE3').count(),
            },
            'by_activity_type': {
                activity: records.filter(activity_type=activity).count()
                for activity, _ in NormalizedRecord.ACTIVITY_TYPES
            }
        }

        return Response(summary)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        record = self.get_object()
        serializer = RecordReviewSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(NormalizedRecordSerializer(record).data)