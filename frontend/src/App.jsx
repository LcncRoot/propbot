import React, { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [grants, setGrants] = useState([]);
  const [selectedGrant, setSelectedGrant] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const handleSearch = () => {
    setLoading(true);
    setError(null);

    fetch(`/api/search?query=${query}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data.matches)) {
          setGrants(data.matches);
          setSelectedGrant(null);
        } else {
          setError("Invalid search response: Expected an array.");
        }
      })
      .catch(() => setError("Search failed. Please try again."))
      .finally(() => setLoading(false));
  };

  const fetchFullDetails = (opportunityId) => {
    setLoadingDetails(true);
    setError(null);

    fetch(`/api/grant/${opportunityId}?fetch_details=true`)
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
        } else {
          setSelectedGrant(data);
        }
      })
      .catch(() => setError("Failed to fetch full details."))
      .finally(() => setLoadingDetails(false));
  };

  return (
    <div>
      <header style={{ backgroundColor: "#007bff", color: "white", padding: "10px" }}>
        <h1>Grant Explorer</h1>
        <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search grants..." />
        <button onClick={handleSearch}>Search</button>
      </header>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {loading && <p>Loading results...</p>}

      <div style={{ display: "flex" }}>
        <div style={{ width: "40%", padding: "10px" }}>
          {grants.length > 0 && <h2>Search Results</h2>}
          <ul>
            {grants.map((grant) => (
              <li key={grant.opportunity_id}>
                <strong>{grant.title}</strong> <br />
                <button onClick={() => fetchFullDetails(grant.opportunity_id)}>Get Full Details</button>
              </li>
            ))}
          </ul>
        </div>

        <div style={{ width: "60%", padding: "10px" }}>
          {selectedGrant && <div><h2>{selectedGrant.title}</h2><p>{selectedGrant.description}</p></div>}
        </div>
      </div>
    </div>
  );
}

export default App;
