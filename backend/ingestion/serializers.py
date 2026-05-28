from rest_framework import serializers
from .models import DataSource, RawDataFile


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ['id', 'name', 'source_type', 'config', 'created_at']


class RawDataFileSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_type = serializers.CharField(source='source.source_type', read_only=True)

    class Meta:
        model = RawDataFile
        fields = ['id', 'source', 'source_name', 'source_type', 'file_name', 'status', 'error_message', 'uploaded_at', 'processed_at']
        read_only_fields = ['status', 'error_message', 'uploaded_at', 'processed_at']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    source_id = serializers.UUIDField()

    def create(self, validated_data):
        from django.core.files.base import ContentFile
        file = validated_data.pop('file')
        source = validated_data.pop('source_id')

        raw_file = RawDataFile.objects.create(
            source_id=source,
            uploaded_file=file,
            file_name=file.name
        )
        return raw_file