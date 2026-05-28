from rest_framework import serializers
from .models import NormalizedRecord


class NormalizedRecordSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)

    class Meta:
        model = NormalizedRecord
        fields = [
            'id', 'source_name', 'activity_type', 'scope', 'amount',
            'original_amount', 'original_unit', 'normalized_unit',
            'emission_factor', 'emission_factor_source', 'start_date',
            'end_date', 'facility_code', 'facility_name', 'description',
            'suspicious_flag', 'suspicious_reason', 'review_status',
            'reviewed_by', 'reviewed_at', 'source_reference',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['amount', 'normalized_unit', 'created_at', 'updated_at']


class RecordReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalizedRecord
        fields = ['id', 'review_status', 'suspicious_flag', 'reviewed_by']

    def update(self, instance, validated_data):
        instance.review_status = validated_data.get('review_status', instance.review_status)
        instance.reviewed_by = validated_data.get('reviewed_by', instance.reviewed_by)
        if instance.review_status in ['APPROVED', 'REJECTED']:
            instance.reviewed_at = serializers.fields.now()
        instance.save()
        return instance