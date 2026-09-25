import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [metrics, setMetrics] = useState({
    total_runs: 0,
    average_execution_time_ms: 0,
  });

  const [history, setHistory] = useState([]);

  const fetchData = async () => {
    try {
      const metricsResponse = await fetch(
        "http://127.0.0.1:8000/api/metrics"
      );
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData);

      const historyResponse = await fetch(
        "http://127.0.0.1:8000/api/history"
      );
      const historyData = await historyResponse.json();
      setHistory(historyData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();

    const interval = setInterval(() => {
      fetchData();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        textAlign: "center",
        padding: "30px",
        fontFamily: "Arial",
      }}
    >
      <h1>WasmBox Dashboard</h1>

      <h2>Metrics</h2>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "20px",
          marginBottom: "30px",
        }}
      >
        <div
          style={{
            border: "1px solid gray",
            padding: "20px",
            width: "180px",
          }}
        >
          <h3>Total Runs</h3>
          <p>{metrics.total_runs}</p>
        </div>

        <div
          style={{
            border: "1px solid gray",
            padding: "20px",
            width: "250px",
          }}
        >
          <h3>Average Execution Time</h3>
          <p>{metrics.average_execution_time_ms} ms</p>
        </div>
      </div>

      <button onClick={fetchData}>Refresh</button>

      <h2 style={{ marginTop: "40px" }}>Execution History</h2>

      {history.length === 0 ? (
        <p>No executions found</p>
      ) : (
        <ul
          style={{
            listStyle: "none",
            padding: 0,
          }}
        >
          {history.map((item, index) => (
            <li
              key={index}
              style={{
                border: "1px solid #ccc",
                margin: "10px auto",
                padding: "10px",
                maxWidth: "700px",
              }}
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;