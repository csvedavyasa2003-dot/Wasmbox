import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [metrics, setMetrics] = useState({
    total_runs: 0,
    average_execution_time_ms: 0,
  });

  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  const API_BASE = "http://127.0.0.1:8000";

  const loadData = async () => {
    try {
      setError("");

      const metricsResponse = await fetch(`${API_BASE}/api/metrics`);
      const historyResponse = await fetch(`${API_BASE}/api/history`);

      if (!metricsResponse.ok || !historyResponse.ok) {
        throw new Error("Failed to fetch data");
      }

      const metricsData = await metricsResponse.json();
      const historyData = await historyResponse.json();

      setMetrics(metricsData);
      setHistory(historyData);
    } catch (err) {
      console.error(err);
      setError("Unable to connect to backend.");
    }
  };

  useEffect(() => {
    loadData();

    const interval = setInterval(() => {
      loadData();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      <h1>WasmBox Dashboard</h1>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <h2>Metrics</h2>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "20px",
          marginBottom: "30px",
          flexWrap: "wrap",
        }}
      >
        <div
          style={{
            border: "1px solid #ccc",
            padding: "20px",
            minWidth: "220px",
            borderRadius: "10px",
          }}
        >
          <h3>Total Runs</h3>
          <p>{metrics.total_runs}</p>
        </div>

        <div
          style={{
            border: "1px solid #ccc",
            padding: "20px",
            minWidth: "220px",
            borderRadius: "10px",
          }}
        >
          <h3>Average Execution Time</h3>
          <p>{metrics.average_execution_time_ms.toFixed(2)} ms</p>
        </div>
      </div>

      <button onClick={loadData}>Refresh</button>

      <h2 style={{ marginTop: "40px" }}>Execution History</h2>

      {history.length === 0 ? (
        <p>No execution history found.</p>
      ) : (
        <div>
          {history.map((item, index) => (
            <div
              key={index}
              style={{
                border: "1px solid #ddd",
                margin: "10px auto",
                padding: "10px",
                maxWidth: "900px",
                borderRadius: "8px",
              }}
            >
              <strong>{item.module_name}</strong>

              <p>
                Inputs: a={item.input_a}, b={item.input_b}
              </p>

              <p>Output: {item.output}</p>

              <p>
                Execution Time: {item.execution_time_ms?.toFixed(2)} ms
              </p>

              <p>
                Executed At:{" "}
                {item.executed_at
                  ? new Date(item.executed_at).toLocaleString()
                  : "N/A"}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;