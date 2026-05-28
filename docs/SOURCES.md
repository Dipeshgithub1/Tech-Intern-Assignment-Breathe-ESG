# Source Research

## 1. SAP Export Format

### Research Findings
SAP exports come in multiple formats:
- **IDoc**: SAP's native XML-based format. Hierarchical segments. Requires SAP middleware expertise.
- **OData**: RESTful API for newer S/4HANA systems. Requires OAuth setup.
- **Flat file CSV**: Most common for analytics. Exported via transaction SE16 or Fiori reports.

### Chosen Format: Flat File CSV
Based on SAP community research (help.sap.com forums), CSV exports are the most common handoff method for emissions data because:
1. Finance/stewardship teams run reports monthly
2. Data is flat enough for direct analysis
3. No middleware required

### Sample Data Structure
```csv
DocumentNumber,Buchdatum,Material,Menge,Mengeneinheit,Plant,PlantName,Waehrung,Betrag,Description
80012345,15.01.2024,DIESEL,1500,GLLO,PLANT001,"Refinery Terminal A",USD,4500.00
```

- `Buchdatum`: German for "posting date" - common in European SAP configurations
- `GLLO`/`LTR`: SAP unit codes (Gallons, Liters)
- Plant codes are internal identifiers requiring lookup tables

### What Would Break in Production
1. Different SAP systems use different field names (some use English headers)
2. Unit codes vary by configuration
3. Missing material master data for emissions factor lookup
4. Date formats vary (DD.MM.YYYY vs YYYY-MM-DD)

---

## 2. Utility Electricity Data

### Research Findings
From UtilityAPI and energy benchmarking docs:
- Utilities provide CSV exports via customer portals
- EPA eGRID data shows typical fields: account_number, meter_number, kWh, demand, billing period
- 3,000+ US utilities each with slightly different formats

### Chosen Format: Portal CSV Export
Most facilities teams download portal exports monthly. Even utilities with APIs often have manual approval steps.

### Sample Data Structure
```csv
account_number,meter_number,kwh,demand_kW,period_start,period_end,utility_company,service_address
ELEC-1001,MTR-001,12500,450,2024-01-01,2024-01-31,"Pacific Gas & Electric","123 Main St, San Francisco, CA"
```

Note: Billing periods vary (28-31 days). Some utilities bill mid-month.

### What Would Break in Production
1. Different utilities use different column names
2. Some include tier rates requiring kWh segmentation
3. Multi-meter accounts need aggregation logic
4. Time-of-use rates require hourly data (not in monthly exports)

---

## 3. Corporate Travel Data

### Research Findings
From Concur and Navan API docs:
- Concur uses Expense API with OAuth2 authentication
- Navan/TripActions uses REST API returning booking records
- Both provide fields: booking_id, type, amount, dates, origin/destination

### Chosen Format: CSV Booking Export
Matches Navan's `/v1/bookings` endpoint schema. Simplifies ingestion.

### Sample Data Structure
```csv
booking_id,booking_type,amount,currency,start_date,end_date,traveler_name,department,origin,destination,distance_miles
TRP-001,FLIGHT,1250,USD,2024-01-08,2024-01-08,"John Smith","Operations",SFO,JFK,2600
```

- Flight distances calculated from airport codes
- Hotels use nights field
- Ground transport uses miles

### What Would Break in Production
1. Not all systems provide distances (need airport database)
2. Multi-city itineraries require segment parsing
3. Hotel nights not always available (need date math)
4. Car rentals vs rideshare need different emission factors