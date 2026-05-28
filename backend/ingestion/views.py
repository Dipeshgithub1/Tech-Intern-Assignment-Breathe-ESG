from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import datetime, date
import csv
import io
from .models import DataSource, RawDataFile
from .serializers import DataSourceSerializer, RawDataFileSerializer, FileUploadSerializer
from emissions.models import NormalizedRecord
from emissions.serializers import NormalizedRecordSerializer


class DataSourceViewSet(viewsets.ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant_id = self.request.query_params.get('tenant')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        return queryset


class RawDataFileViewSet(viewsets.ModelViewSet):
    queryset = RawDataFile.objects.all().select_related('source')
    serializer_class = RawDataFileSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant_id = self.request.query_params.get('tenant')
        if tenant_id:
            queryset = queryset.filter(source__tenant_id=tenant_id)
        return queryset

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        raw_file = self.get_object()
        return self._process_file(raw_file)

    def _process_file(self, raw_file):
        source_type = raw_file.source.source_type

        try:
            if source_type == 'SAP':
                records = self._process_sap(raw_file)
            elif source_type == 'UTILITY':
                records = self._process_utility(raw_file)
            elif source_type == 'TRAVEL':
                records = self._process_travel(raw_file)
            else:
                raise ValueError(f"Unknown source type: {source_type}")

            raw_file.status = 'PROCESSED'
            raw_file.save()

            return Response({
                'status': 'processed',
                'records_created': len(records)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            raw_file.status = 'FAILED'
            raw_file.error_message = str(e)[:500]
            raw_file.save()
            return Response({
                'status': 'failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_sap(self, raw_file):
        records = []
        if not raw_file.uploaded_file:
            return records

        content = raw_file.uploaded_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))

        for row in reader:
            try:
                record = NormalizedRecord.objects.create(
                    tenant=raw_file.source.tenant,
                    source=raw_file.source,
                    raw_file=raw_file,
                    original_row_id=row.get('DocumentNumber', ''),
                    activity_type=self._map_sap_activity(row),
                    scope=self._map_sap_scope(row),
                    original_amount=self._parse_float(row.get('Menge', 0)),
                    original_unit=row.get('Mengeneinheit', ''),
                    amount=self._convert_sap_to_co2e(row),
                    start_date=self._parse_date(row.get('Buchdatum', '')),
                    end_date=self._parse_date(row.get('Buchdatum', '')),
                    facility_code=row.get('Plant', ''),
                    facility_name=row.get('PlantName', ''),
                    description=row.get('Description', ''),
                    source_reference=f"SAP-{row.get('DocumentNumber', '')}",
                    suspicious_flag=self._detect_sap_suspicious(row)
                )
                records.append(record)
            except Exception:
                continue

        return records

    def _process_utility(self, raw_file):
        records = []
        if not raw_file.uploaded_file:
            return records

        content = raw_file.uploaded_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))

        for row in reader:
            try:
                record = NormalizedRecord.objects.create(
                    tenant=raw_file.source.tenant,
                    source=raw_file.source,
                    raw_file=raw_file,
                    original_row_id=row.get('account_number', ''),
                    activity_type='ELECTRICITY',
                    scope='SCOPE2',
                    original_amount=self._parse_float(row.get('kwh', 0)),
                    original_unit='kWh',
                    amount=self._parse_float(row.get('kwh', 0)) * 0.45,
                    emission_factor=0.45,
                    emission_factor_source='EPA eGRID 2023 national average',
                    start_date=self._parse_date(row.get('period_start', '')),
                    end_date=self._parse_date(row.get('period_end', '')),
                    facility_code=row.get('meter_number', ''),
                    facility_name=row.get('service_address', ''),
                    description=row.get('utility_company', ''),
                    source_reference=f"UTILITY-{row.get('account_number', '')}",
                    suspicious_flag=self._detect_utility_suspicious(row)
                )
                records.append(record)
            except Exception:
                continue

        return records

    def _process_travel(self, raw_file):
        records = []
        if not raw_file.uploaded_file:
            return records

        content = raw_file.uploaded_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))

        for row in reader:
            try:
                activity_type, scope = self._map_travel_activity(row)
                record = NormalizedRecord.objects.create(
                    tenant=raw_file.source.tenant,
                    source=raw_file.source,
                    raw_file=raw_file,
                    original_row_id=row.get('booking_id', ''),
                    activity_type=activity_type,
                    scope=scope,
                    original_amount=self._parse_float(row.get('amount', 0)),
                    original_unit='USD',
                    amount=self._calculate_travel_emissions(row, activity_type),
                    emission_factor=self._get_travel_emission_factor(activity_type),
                    emission_factor_source='DEFRA 2024',
                    start_date=self._parse_date(row.get('start_date', '')),
                    end_date=self._parse_date(row.get('end_date', '')),
                    facility_code=row.get('department', ''),
                    facility_name=row.get('traveler_name', ''),
                    description=row.get('description', ''),
                    source_reference=f"TRAVEL-{row.get('booking_id', '')}",
                    suspicious_flag=self._detect_travel_suspicious(row)
                )
                records.append(record)
            except Exception:
                continue

        return records

    def _map_sap_activity(self, row):
        material = row.get('Material', '').lower()
        if 'diesel' in material or 'fuel' in material:
            return 'FUEL'
        return 'PROCUREMENT'

    def _map_sap_scope(self, row):
        activity = self._map_sap_activity(row)
        if activity == 'FUEL':
            return 'SCOPE1'
        return 'SCOPE3'

    def _convert_sap_to_co2e(self, row):
        amount = self._parse_float(row.get('Menge', 0))
        material = row.get('Material', '').lower()

        if 'diesel' in material:
            return amount * 10.18  # kg CO2e per gallon
        elif 'gasoline' in material:
            return amount * 8.89
        return amount * 0.5

    def _detect_sap_suspicious(self, row):
        amount = self._parse_float(row.get('Menge', 0))
        return amount > 10000 or amount <= 0

    def _parse_float(self, value):
        try:
            return float(str(value).replace(',', '').replace('"', ''))
        except (ValueError, TypeError):
            return 0.0

    def _parse_date(self, date_str):
        if not date_str:
            return date.today()
        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y', '%Y/%m/%d']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return date.today()

    def _map_travel_activity(self, row):
        booking_type = row.get('booking_type', 'FLIGHT').upper()
        scope_map = {
            'FLIGHT': ('FLIGHT', 'SCOPE3'),
            'HOTEL': ('HOTEL', 'SCOPE3'),
            'CAR': ('GROUND_TRANSPORT', 'SCOPE1'),
            'RIDE': ('GROUND_TRANSPORT', 'SCOPE3'),
            'TRAIN': ('GROUND_TRANSPORT', 'SCOPE3'),
        }
        return scope_map.get(booking_type, ('FLIGHT', 'SCOPE3'))

    def _calculate_travel_emissions(self, row, activity_type):
        amount = self._parse_float(row.get('amount', 0))
        booking_type = row.get('booking_type', 'FLIGHT').upper()

        if booking_type == 'FLIGHT':
            distance = self._parse_float(row.get('distance_miles', 0))
            if distance > 0:
                return distance * 0.254  # kg CO2e per mile
            return amount * 0.15

        if booking_type == 'HOTEL':
            nights = self._parse_float(row.get('nights', 1))
            return nights * 25  # kg CO2e per night

        return amount * 0.1

    def _get_travel_emission_factor(self, activity_type):
        factors = {
            'FLIGHT': 0.254,
            'HOTEL': 25,
            'GROUND_TRANSPORT': 0.1
        }
        return factors.get(activity_type, 0.1)

    def _detect_travel_suspicious(self, row):
        amount = self._parse_float(row.get('amount', 0))
        return amount > 5000 or amount <= 0