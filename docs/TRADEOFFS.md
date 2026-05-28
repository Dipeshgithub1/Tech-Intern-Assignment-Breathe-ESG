# Tradeoffs

## What Was Deliberately Not Built

### 1. No Authentication/Authorization
- **What**: Open API endpoints, no login required
- **Why**: MVP focus. Authentication adds significant complexity for both Django and React. Would use JWT or Django session auth in production.
- **Risk**: Anyone can query/modify data.

### 2. No Background Processing
- **What**: File processing happens synchronously in request thread
- **Why**: Simple for prototype. Large files would timeout.
- **Risk**: Timeout on large SAP exports. Production would use Celery/RQ.

### 3. No Unit Conversion Service
- **What**: Hardcoded conversion factors in ingestion logic
- **Why**: No shared unit library exists. Would integrate with EPA or GHG Protocol factors.
- **Risk**: Inconsistent or outdated factors.

### 4. No Facility Code Mapping
- **What**: Plant codes stored as-is without lookup
- **Why**: Would require client-specific mapping tables.
- **Risk**: Analysts see cryptic codes.

### 5. No Emission Factor Versioning
- **What**: Factors stored per-record without source tracking
- **Why**: Adds DB complexity for MVP.
- **Risk**: Can't audit methodology changes.