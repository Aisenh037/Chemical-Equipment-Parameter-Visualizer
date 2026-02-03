import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import { Upload, FileText, Activity, Database, History, Download } from 'lucide-react';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE = 'http://localhost:8000/api/equipment';
const AUTH_HEADER = {
  Authorization: 'Basic ' + btoa('admin:password123')
};

function App() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/history/`, { headers: AUTH_HEADER });
      setHistory(res.data);
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/upload/`, formData, {
        headers: {
          ...AUTH_HEADER,
          'Content-Type': 'multipart/form-data'
        }
      });
      setData(res.data);
      fetchHistory();
    } catch (err) {
      setError(err.response?.data?.error || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = (id) => {
    window.open(`${API_BASE}/report/${id}/`, '_blank');
  };

  const renderCharts = () => {
    if (!data || !data.summary) return null;

    const barData = {
      labels: ['Flowrate', 'Pressure', 'Temperature'],
      datasets: [
        {
          label: 'Average Parameters',
          data: [
            data.summary.averages.flowrate,
            data.summary.averages.pressure,
            data.summary.averages.temperature
          ],
          backgroundColor: 'rgba(99, 102, 241, 0.6)',
          borderColor: 'rgba(99, 102, 241, 1)',
          borderWidth: 1,
        },
      ],
    };

    const pieData = {
      labels: Object.keys(data.summary.type_distribution),
      datasets: [
        {
          data: Object.values(data.summary.type_distribution),
          backgroundColor: [
            '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308'
          ],
        },
      ],
    };

    return (
      <div className="grid">
        <div className="card">
          <h3>Average Parameters</h3>
          <Bar data={barData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
        </div>
        <div className="card">
          <h3>Equipment Type Distribution</h3>
          <Pie data={pieData} options={{ responsive: true }} />
        </div>
      </div>
    );
  };

  return (
    <div className="container">
      <header>
        <div>
          <h1>EquiViz Pro</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Chemical Equipment Parameter Visualizer</p>
        </div>
        <Activity color="var(--primary)" size={32} />
      </header>

      <div className="grid" style={{ gridTemplateColumns: '1fr 2fr' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Upload size={20} color="var(--primary)" />
            <h3 style={{ margin: 0 }}>Upload Data</h3>
          </div>
          <input
            type="file"
            onChange={handleFileChange}
            accept=".csv"
            style={{ marginBottom: '1rem', width: '100%', color: 'var(--text-muted)' }}
          />
          <button className="btn" onClick={handleUpload} disabled={loading} style={{ width: '100%' }}>
            {loading ? 'Processing...' : 'Analyze CSV'}
          </button>
          {error && <p style={{ color: 'var(--danger)', marginTop: '0.5rem', fontSize: '0.8rem' }}>{error}</p>}
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <History size={20} color="var(--primary)" />
            <h3 style={{ margin: 0 }}>Recent Uploads</h3>
          </div>
          <div style={{ maxHeight: '150px', overflowY: 'auto' }}>
            {history.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No history available</p>
            ) : (
              <table style={{ marginTop: 0 }}>
                <tbody>
                  {history.map(item => (
                    <tr key={item.id}>
                      <td>{item.file_name}</td>
                      <td>{new Date(item.uploaded_at).toLocaleString()}</td>
                      <td style={{ textAlign: 'right' }}>
                        <button className="btn btn-outline" size="sm" onClick={() => downloadReport(item.id)}>
                          <Download size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {data && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{data.summary.total_count}</div>
              <div className="stat-label">Total Equipment</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{data.summary.averages.flowrate}</div>
              <div className="stat-label">Avg Flowrate</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{data.summary.averages.pressure}</div>
              <div className="stat-label">Avg Pressure (bar)</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{data.summary.averages.temperature}</div>
              <div className="stat-label">Avg Temp (°C)</div>
            </div>
          </div>

          {renderCharts()}

          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <Database size={20} color="var(--primary)" />
              <h3 style={{ margin: 0 }}>Equipment Details</h3>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Flowrate</th>
                    <th>Pressure</th>
                    <th>Temperature</th>
                  </tr>
                </thead>
                <tbody>
                  {data.data.map((row, i) => (
                    <tr key={i}>
                      <td>{row['Equipment Name']}</td>
                      <td>{row['Type']}</td>
                      <td>{row['Flowrate']}</td>
                      <td>{row['Pressure']}</td>
                      <td>{row['Temperature']}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
