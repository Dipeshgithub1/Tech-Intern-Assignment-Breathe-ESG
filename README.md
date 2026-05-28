# Breathe ESG - Emissions Data Review Dashboard

A prototype Django REST + React application for ingesting emissions data from SAP, utility portals, and travel platforms, normalizing it, and providing an analyst review workflow.

## Live Demo
- Backend API: `/api/`
- React Dashboard: `/`

## Quick Start

```bash
# Backend (Django)
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (React/Vite)
cd frontend
npm install
npm run dev
```

## Architecture

- **Django REST Framework** for API endpoints
- **React** with hooks for the dashboard UI
- **SQLite** for storage (production would use PostgreSQL)
- **Whitenoise** for static file serving in production

## Data Sources

1. **SAP** - Fuel/procurement exports (CSV format)
2. **Utility** - Electricity consumption (portal CSV exports)  
3. **Travel** - Business travel bookings (CSV format)

## API Endpoints

- `/api/tenants/` - Company tenant management
- `/api/data-sources/` - Source configuration
- `/api/raw-files/` - File upload and processing
- `/api/records/` - Normalized emission records
- `/api/records/summary/` - Aggregated statistics

## Review Workflow

1. Upload CSV file to a configured data source
2. Records are auto-processed and flagged for suspicious values
3. Analyst reviews PENDING records and approves/rejects
4. Approved records are locked for auditor review

## Documentation

- `docs/MODEL.md` - Data model design
- `docs/DECISIONS.md` - Implementation choices
- `docs/TRADEOFFS.md` - What was intentionally not built
- `docs/SOURCES.md` - Source format research