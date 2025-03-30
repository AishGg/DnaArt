import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [sequence, setSequence] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError("");
    setResult(null);
    setLoading(true);

    try {
      const response = await axios.post(
        `${VITE_REACT_APP_API_URL}/analyze-dna`,
        { sequence },
        { headers: { "Content-Type": "application/json" } }
      );
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to connect to the backend. Is it running?");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value.toUpperCase().replace(/[^ATCG]/g, "");
    setSequence(value);
  };

  const handleReset = () => {
    setSequence("");
    setResult(null);
    setError("");
    setLoading(false);
  };

  return (
    <div className="app">
      <button className="reset-button" onClick={handleReset}>
        New DNA
      </button>
      <h1>DNA Art</h1>
      <h2>Welcome, DNA Dreamers!</h2>
      <p>Enter your DNA sequence below and watch your genetic code transform into unique art!</p>

      {!result && !loading && (
        <div className="input-container">
          <input
            type="text"
            placeholder="Enter your 40-character DNA sequence..."
            value={sequence}
            onChange={handleInputChange}
            maxLength={40}
          />
          <p>{sequence.length}/40 characters</p>
          <button onClick={handleSubmit} disabled={sequence.length !== 40}>
            Generate
          </button>
        </div>
      )}

      {loading && <div id="loading">Searching your DNA vibes... 🔍</div>}
      {error && <p className="error">{error}</p>}
      {result && (
        <div id="output">
          <div className="result-container">
            <div className="image-container">
              <h3>Your DNA Art</h3>
              <img
                src={`${VITE_REACT_APP_API_URL}/${result.image_url}?t=${Date.now()}`}
                alt="DNA Art"
                onError={() => setError("Image failed to load.")}
              />
              <a href={`${VITE_REACT_APP_API_URL}/${result.image_url}`} download>Download Art</a>
            </div>
            <div className="description-container">
              <h3>Your Genetic Story</h3>
              <p>{result.description}</p>
            </div>
          </div>
        </div>
      )}

      {/* Floating circles */}
      <div className="floating" style={{ width: "100px", height: "100px", top: "10%", left: "20%" }}></div>
      <div className="floating" style={{ width: "150px", height: "150px", top: "50%", left: "70%" }}></div>
      <div className="floating" style={{ width: "80px", height: "80px", top: "80%", left: "30%" }}></div>
    </div>
  );
}

export default App;