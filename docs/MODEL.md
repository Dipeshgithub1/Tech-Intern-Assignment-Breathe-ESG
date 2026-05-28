# Data Model

## Overview

The data model centers around `NormalizedRecord` - a unified representation of all emissions data regardless of source. This design prioritizes auditability and analyst workflow over normalized database purity.

## Core Entities

### Tenant
Multi-tenancy support. Each tenant represents a client company. All data is isolated by tenant.

### DataSource
Represents an integration endpoint. Types: SAP, UTILITY, TRAVEL. Contains source-specific configuration for field mappings and parsing rules.

### RawDataFile
Tracks uploaded files and their processing status. Stores file metadata and any parsing errors.

### NormalizedRecord
The central entity. Each record represents a normalized emission activity with:

- **Scope classification**: Explicit SCOPE1/2/3 categorization
- **Source tracking**: Links back to original DataSource and RawDataFile
- **Amount normalization**: Original amount/unit preserved alongside normalized kg CO2e
- **Temporal bounds**: start_date/end_date for billing/activity periods
- **Facility context**: plant codes mapped to facility names
- **Review workflow**: PENDING/APPROVED/REJECTED status with reviewer tracking
- **Suspicious flagging**: Auto-flagged on outlier detection with reason

### AuditLog
Immutable log of all changes to records. Captures old/new values, change type, and actor.

## Key Design Decisions

1. **No separate emission factor table**: Factors are embedded in records for simplicity. In production, this would be a reference table with versioning.

2. **Date ranges for billing periods**: Utility and travel data often span periods that don't align with calendar months.

3. **Raw row preservation via source_reference**: Analysts can trace anomalies back to source documents.

4. **Suspicious flag on record**: Enables quick triage without blocking ingestion.

5. **Tenant isolation at query level**: All endpoints filter by tenant, enforced in views.