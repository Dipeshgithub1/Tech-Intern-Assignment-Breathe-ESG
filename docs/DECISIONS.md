# Decisions Log

## Source Format Choices

### SAP
- **Chose**: Flat file CSV export (not IDoc or OData)
- **Why**: Most enterprises export to CSV for analytics. IDoc is SAP-specific XML that requires middleware; CSV is universal.
- **Subset handled**: Material purchases (fuel, lubricants) and procurement
- **Ignored**: Production planning, inventory movements, financial documents

### Utility Data
- **Chose**: Portal CSV export
- **Why**: Most utilities don't have public APIs. Portal exports are the standard handoff method.
- **Subset handled**: Electricity consumption (kWh) with demand charges
- **Ignored**: Natural gas, water, multi-meter billing complexities

### Travel Platform
- **Chose**: CSV booking export (matching Navan/Fivetran schema)
- **Why**: Mirrors what most travel platforms export. Simpler than Concur's OAuth API dance.
- **Subset handled**: Flights, hotels, ground transport
- **Ignored**: Train tickets, ride-sharing details, receipt parsing

## Technical Decisions

### Unit Normalization
- **Chose**: Convert everything to kg CO2e at ingest time
- **Why**: Analysts shouldn't do math. Store conversion factors for audit trail.
- **Tradeoff**: Can't retroactively apply improved factors.

### Audit Trail
- **Chose**: Separate AuditLog table with JSON diffs
- **Why**: Immutable logs, easy to query, flexible for any field changes.

### Suspicious Detection
- **Chose**: Simple thresholds (amount > 10000 or <= 0)
- **Why**: MVP. Real system would use statistical outlier detection.

## Questions for PM

1. Should we support recurring file uploads per source, or one-time ingestion?
2. Do clients have existing facility/plant code lookup tables we should import?
3. What emission factor methodology (GHG Protocol, Defra, EPA eGRID) to use?
4. Do auditors need to see the original file, or just the normalized records?
5. Should rejected records be retained for audit trail?