import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = '/api'

function App() {
  const [tenantId, setTenantId] = useState(null)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [summary, setSummary] = useState({})
  const [records, setRecords] = useState([])
  const [sources, setSources] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedSource, setSelectedSource] = useState(null)

  useEffect(() => {
    const initTenant = async () => {
      try {
        const response = await axios.get(`${API_BASE}/tenants/`)
        if (response.data.length > 0) {
          setTenantId(response.data[0].id)
        } else {
          const createResponse = await axios.post(`${API_BASE}/tenants/`, {
            company_name: 'Demo Corporation'
          })
          setTenantId(createResponse.data.id)
        }
      } catch (error) {
        console.error('Error initializing tenant:', error)
      }
    }
    initTenant()
  }, [])

  useEffect(() => {
    if (tenantId) {
      fetchSummary()
      fetchRecords()
      fetchSources()
    }
  }, [tenantId])

  const fetchSummary = async () => {
    try {
      const response = await axios.get(`${API_BASE}/records/summary/?tenant=${tenantId}`)
      setSummary(response.data)
    } catch (error) {
      console.error('Error fetching summary:', error)
    }
  }

  const fetchRecords = async (status = 'PENDING') => {
    try {
      const response = await axios.get(`${API_BASE}/records/?tenant=${tenantId}&status=${status}`)
      setRecords(response.data)
    } catch (error) {
      console.error('Error fetching records:', error)
    }
  }

  const fetchSources = async () => {
    try {
      const response = await axios.get(`${API_BASE}/data-sources/?tenant=${tenantId}`)
      setSources(response.data)
      if (response.data.length > 0 && !selectedSource) {
        setSelectedSource(response.data[0].id)
      }
    } catch (error) {
      console.error('Error fetching sources:', error)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file || !selectedSource) return

    const formData = new FormData()
    formData.append('file', file)
    formData.append('source_id', selectedSource)

    try {
      const response = await axios.post(`${API_BASE}/raw-files/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      await axios.post(`${API_BASE}/raw-files/${response.data.id}/process/`)
      fetchSummary()
      fetchRecords()
    } catch (error) {
      console.error('Error uploading file:', error)
    }
  }

  const handleReview = async (recordId, status) => {
    try {
      await axios.post(`${API_BASE}/records/${recordId}/review/`, {
        review_status: status,
        reviewed_by: 'analyst'
      })
      fetchSummary()
      fetchRecords()
    } catch (error) {
      console.error('Error reviewing record:', error)
    }
  }

  const createDataSource = async (type, name) => {
    try {
      await axios.post(`${API_BASE}/data-sources/`, {
        tenant: tenantId,
        source_type: type,
        name: name
      })
      fetchSources()
    } catch (error) {
      console.error('Error creating data source:', error)
    }
  }

  const ScopeBadge = ({ scope }) => {
    const colors = {
      SCOPE1: '#ef4444',
      SCOPE2: '#3b82f6',
      SCOPE3: '#10b981'
    }
    return <span className="scope-badge" style={{backgroundColor: colors[scope]}}>{scope.replace('SCOPE', 'Scope ')}</span>
  }

  const ActivityIcon = ({ type }) => {
    const icons = {
      FUEL: '⛽',
      ELECTRICITY: '⚡',
      FLIGHT: '✈️',
      HOTEL: '🏨',
      GROUND_TRANSPORT: '🚗',
      PROCUREMENT: '📦'
    }
    return <span className="activity-icon">{icons[type] || '📊'}</span>
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Breathe ESG - Data Review Dashboard</h1>
        <nav className="tabs">
          <button className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>Dashboard</button>
          <button className={activeTab === 'upload' ? 'active' : ''} onClick={() => setActiveTab('upload')}>Upload Data</button>
          <button className={activeTab === 'review' ? 'active' : ''} onClick={() => { setActiveTab('review'); fetchRecords('PENDING') }}>Pending Review</button>
          <button className={activeTab === 'approved' ? 'active' : ''} onClick={() => { setActiveTab('approved'); fetchRecords('APPROVED') }}>Approved</button>
          <button className={activeTab === 'rejected' ? 'active' : ''} onClick={() => { setActiveTab('rejected'); fetchRecords('REJECTED') }}>Rejected</button>
        </nav>
      </header>

      <main className="main">
        {activeTab === 'dashboard' && (
          <div className="dashboard">
            <div className="summary-cards">
              <div className="card">
                <h3>Total Records</h3>
                <p className="stat">{summary.total || 0}</p>
              </div>
              <div className="card">
                <h3>Pending Review</h3>
                <p className="stat">{summary.pending || 0}</p>
              </div>
              <div className="card">
                <h3>Approved</h3>
                <p className="stat">{summary.approved || 0}</p>
              </div>
              <div className="card warning">
                <h3>Suspicious</h3>
                <p className="stat">{summary.suspicious || 0}</p>
              </div>
            </div>

            <div className="scope-breakdown">
              <h2>By Scope</h2>
              <div className="scopes">
                <div className="scope-item">
                  <ScopeBadge scope="SCOPE1" />
                  <span>{summary.by_scope?.scope1 || 0} records</span>
                </div>
                <div className="scope-item">
                  <ScopeBadge scope="SCOPE2" />
                  <span>{summary.by_scope?.scope2 || 0} records</span>
                </div>
                <div className="scope-item">
                  <ScopeBadge scope="SCOPE3" />
                  <span>{summary.by_scope?.scope3 || 0} records</span>
                </div>
              </div>
            </div>

            <div className="sources-section">
              <h2>Data Sources</h2>
              <div className="sources">
                <button onClick={() => createDataSource('SAP', 'SAP Fuel & Procurement')}>+ Add SAP Source</button>
                <button onClick={() => createDataSource('UTILITY', 'Utility Portal')}>+ Add Utility Source</button>
                <button onClick={() => createDataSource('TRAVEL', 'Travel Platform')}>+ Add Travel Source</button>
              </div>
              <ul className="source-list">
                {sources.map(s => (
                  <li key={s.id} className={s.source_type.toLowerCase()}>
                    <strong>{s.name}</strong> - {s.source_type}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'upload' && (
          <div className="upload-section">
            <h2>Upload Data File</h2>
            <p>Select a data source and upload a CSV file to ingest emissions data.</p>

            <div className="form-group">
              <label>Data Source:</label>
              <select value={selectedSource || ''} onChange={(e) => setSelectedSource(e.target.value)}>
                <option value="">-- Select Source --</option>
                {sources.map(s => (
                  <option key={s.id} value={s.id}>{s.name} ({s.source_type})</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>CSV File:</label>
              <input type="file" accept=".csv" onChange={handleFileUpload} />
            </div>

            <div className="format-info">
              <h3>Expected Formats:</h3>
              <ul>
                <li><strong>SAP:</strong> DocumentNumber, Buchdatum, Material, Menge, Mengeneinheit, Plant, PlantName, Description</li>
                <li><strong>Utility:</strong> account_number, meter_number, kwh, period_start, period_end, service_address, utility_company</li>
                <li><strong>Travel:</strong> booking_id, booking_type, amount, start_date, end_date, traveler_name, department, distance_miles, nights</li>
              </ul>
            </div>
          </div>
        )}

        {(activeTab === 'review' || activeTab === 'approved' || activeTab === 'rejected') && (
          <div className="records-section">
            <h2>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Records</h2>
            <div className="records-list">
              {records.length === 0 ? (
                <p>No records found.</p>
              ) : (
                records.map(record => (
                  <div key={record.id} className={`record-card ${record.suspicious_flag ? 'suspicious' : ''}`}>
                    <div className="record-header">
                      <ActivityIcon type={record.activity_type} />
                      <h3>{record.activity_type.replace('_', ' ')}</h3>
                      <ScopeBadge scope={record.scope} />
                      {record.suspicious_flag && <span className="flag">⚠ Suspicious</span>}
                    </div>

                    <div className="record-details">
                      <div><strong>Amount:</strong> {record.amount?.toFixed(2)} kg CO2e</div>
                      <div><strong>Original:</strong> {record.original_amount} {record.original_unit}</div>
                      <div><strong>Period:</strong> {record.start_date} to {record.end_date}</div>
                      <div><strong>Facility:</strong> {record.facility_name || record.facility_code || '-'}</div>
                      <div><strong>Source:</strong> {record.source_reference}</div>
                      {record.suspicious_reason && <div className="reason"><strong>Reason:</strong> {record.suspicious_reason}</div>}
                    </div>

                    {activeTab === 'review' && (
                      <div className="record-actions">
                        <button className="approve" onClick={() => handleReview(record.id, 'APPROVED')}>Approve</button>
                        <button className="reject" onClick={() => handleReview(record.id, 'REJECTED')}>Reject</button>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App