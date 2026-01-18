import React, { useState } from 'react';
import './styles/globals.css';

function App() {
  const [query, setQuery] = useState("");
  const [grants, setGrants] = useState([]);
  const [contracts, setContracts] = useState([]);
  const [rfis, setRfis] = useState([]);
  const [selectedGrant, setSelectedGrant] = useState(null);
  const [selectedContract, setSelectedContract] = useState(null);
  const [selectedRfi, setSelectedRfi] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [activeTab, setActiveTab] = useState("grants");
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearchInput = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSearch = async (e) => {
    e.preventDefault(); // Prevent form submission
    if (!searchTerm.trim()) return;
    
    setLoading(true);
    console.log('Searching for:', searchTerm); // Debug log
    
    try {
      const response = await fetch(`/api/search?query=${encodeURIComponent(searchTerm)}`);
      const data = await response.json();
      console.log('Search results:', data); // Debug log
      if (data.grants !== undefined && data.contracts !== undefined) {
        setGrants(data.grants);
        setContracts(data.contracts);
        setRfis(data.rfis || []);
        setSelectedGrant(null);
        setSelectedContract(null);
        setSelectedRfi(null);
      } else {
        setError("Invalid search response format.");
      }
    } catch (error) {
      console.error('Error searching:', error);
      setError("Search failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fetchGrantDetails = async (grant) => {
    setLoadingDetails(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/grant/${grant.opportunity_id}?fetch_details=true`);
      if (!response.ok) {
        throw new Error('Failed to fetch grant details');
      }
      const detailedGrant = await response.json();
      console.log('Detailed grant data:', detailedGrant);
      setSelectedGrant(detailedGrant);
    } catch (err) {
      setError('Failed to load grant details. Please try again.');
      console.error('Error fetching grant details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  const fetchContractDetails = async (contract) => {
    setLoadingDetails(true);
    setError(null);

    try {
      const response = await fetch(`/api/contract/${contract.opportunity_id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch contract details');
      }
      const detailedContract = await response.json();
      setSelectedContract(detailedContract);
    } catch (err) {
      setError('Failed to load contract details. Please try again.');
      console.error('Error fetching contract details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  const fetchRfiDetails = async (rfi) => {
    setLoadingDetails(true);
    setError(null);

    try {
      // RFIs use the same contract endpoint since they're from SAM.gov
      const response = await fetch(`/api/contract/${rfi.opportunity_id}`);
      if (!response.ok) {
        throw new Error('Failed to fetch RFI details');
      }
      const detailedRfi = await response.json();
      setSelectedRfi(detailedRfi);
    } catch (err) {
      setError('Failed to load RFI details. Please try again.');
      console.error('Error fetching RFI details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  return (
    <div>
      <header style={{ backgroundColor: "#007bff", color: "white", padding: "15px", textAlign: "center" }}>
        <h1>Funding Explorer</h1>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginTop: '15px' }}>
          <input
            type="text"
            value={searchTerm}
            onChange={handleSearchInput}
            placeholder="Search grants and contracts..."
            style={{ padding: '10px 15px', fontSize: '16px', borderRadius: '4px', border: 'none', width: '300px' }}
          />
          <button type="submit" style={{ padding: '10px 20px', fontSize: '16px', borderRadius: '4px', border: 'none', backgroundColor: '#0056b3', color: 'white', cursor: 'pointer' }}>Search</button>
        </form>
      </header>

      {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}
      {loading && <p style={{ textAlign: "center" }}>Loading results...</p>}

      <div style={{ display: "flex", justifyContent: "center", marginTop: "20px", gap: "10px" }}>
        <button onClick={() => setActiveTab("grants")} style={{ padding: "8px 16px", cursor: "pointer", backgroundColor: activeTab === "grants" ? "#007bff" : "#ccc", color: "white", border: "none", borderRadius: "4px" }}>
          Grants {grants.length > 0 && `(${grants.length})`}
        </button>
        <button onClick={() => setActiveTab("contracts")} style={{ padding: "8px 16px", cursor: "pointer", backgroundColor: activeTab === "contracts" ? "#007bff" : "#ccc", color: "white", border: "none", borderRadius: "4px" }}>
          Contracts {contracts.length > 0 && `(${contracts.length})`}
        </button>
        <button onClick={() => setActiveTab("rfis")} style={{ padding: "8px 16px", cursor: "pointer", backgroundColor: activeTab === "rfis" ? "#007bff" : "#ccc", color: "white", border: "none", borderRadius: "4px" }}>
          RFIs {rfis.length > 0 && `(${rfis.length})`}
        </button>
      </div>

      {activeTab === "grants" && (
        <div style={{ marginTop: "20px", padding: "15px" }}>
          {grants.length > 0 && <h2>Grant Results</h2>}
          <ul style={{ listStyle: "none", padding: 0 }}>
            {grants.map((grant) => (
              <li key={grant.opportunity_id} style={{ marginBottom: "10px", padding: "10px", borderBottom: "1px solid #ddd" }}>
                <p><strong>{grant.title}</strong> ({grant.agency})</p>
                <p><strong>Funding:</strong> ${Number(grant.funding_amount).toLocaleString()}</p>
                <p><strong>Deadline:</strong> {grant.deadline || "N/A"}</p>
                <button onClick={() => fetchGrantDetails(grant)}>View Details</button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {activeTab === "contracts" && (
        <div style={{ marginTop: "20px", padding: "15px" }}>
          {contracts.length > 0 && <h2>SAM Contract Results</h2>}
          {contracts.length === 0 && <p style={{ textAlign: "center", color: "#666" }}>No contracts found. Try a different search term.</p>}
          <ul style={{ listStyle: "none", padding: 0 }}>
            {contracts.map((contract, index) => (
              <li
                key={`${contract.opportunity_id}-${index}`}
                style={{ marginBottom: "10px", padding: "10px", borderBottom: "1px solid #ddd" }}
              >
                <p><strong>{contract.title}</strong></p>
                <p><strong>NAICS Code:</strong> {contract.naics_code || "N/A"}</p>
                <p><strong>Response Deadline:</strong> {contract.response_deadline || "N/A"}</p>
                <button onClick={() => fetchContractDetails(contract)}>View Details</button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {activeTab === "rfis" && (
        <div style={{ marginTop: "20px", padding: "15px" }}>
          {rfis.length > 0 && <h2>RFI / Sources Sought Results</h2>}
          {rfis.length === 0 && <p style={{ textAlign: "center", color: "#666" }}>No RFIs found. Try a different search term.</p>}
          <ul style={{ listStyle: "none", padding: 0 }}>
            {rfis.map((rfi, index) => (
              <li
                key={`${rfi.opportunity_id}-${index}`}
                style={{ marginBottom: "10px", padding: "10px", borderBottom: "1px solid #ddd" }}
              >
                <p><strong>{rfi.title}</strong></p>
                <p><strong>Notice Type:</strong> {rfi.notice_type || "RFI"}</p>
                <p><strong>NAICS Code:</strong> {rfi.naics_code || "N/A"}</p>
                <p><strong>Response Deadline:</strong> {rfi.response_deadline || "N/A"}</p>
                <button onClick={() => fetchRfiDetails(rfi)}>View Details</button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        {selectedGrant && (
          <div style={{ width: '80%', maxWidth: '1000px', padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '8px', marginTop: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h2 style={{ color: 'var(--accent-blue)' }}>{selectedGrant.title}</h2>
            <div style={{ color: 'var(--text-light)' }}>
              <p><strong>Agency:</strong> {selectedGrant.agency}</p>
              <p><strong>Funding Amount:</strong> ${Number(selectedGrant.funding_amount).toLocaleString()}</p>
              <p><strong>Deadline:</strong> {selectedGrant.deadline || "N/A"}</p>
              <p><strong>Opportunity Number:</strong> {selectedGrant.opportunity_number || "N/A"}</p>
              <p><strong>Description:</strong> {selectedGrant.synopsis_description}</p>
              <p><strong>Eligibility:</strong></p>
              <pre style={{ 
                whiteSpace: "pre-wrap", 
                wordWrap: "break-word", 
                background: 'rgba(36, 43, 69, 0.5)', 
                padding: '10px',
                color: 'var(--text-secondary)'
              }}>
                {selectedGrant.eligibility || "N/A"}
              </pre>
              <p><strong>Number of Expected Awards:</strong> {selectedGrant.num_awards || "N/A"}</p>
              <p><strong>Award Ceiling:</strong> ${selectedGrant.award_ceiling || "N/A"}</p>
              <p><strong>Award Floor:</strong> ${selectedGrant.award_floor || "N/A"}</p>
              {selectedGrant.contact_name && (
                <p><strong>Contact:</strong> {selectedGrant.contact_name} - 
                  <a href={`mailto:${selectedGrant.contact_email}`} 
                     style={{ color: 'var(--accent-blue)' }}>
                    {selectedGrant.contact_email}
                  </a>
                </p>
              )}
              {selectedGrant.apply_url && (
                <p>
                  <a href={selectedGrant.apply_url} 
                     target="_blank" 
                     rel="noopener noreferrer"
                     style={{
                       color: 'var(--accent-blue)',
                       textDecoration: 'none',
                       display: 'inline-block',
                       marginTop: '1rem'
                     }}>
                    Apply Here
                  </a>
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {selectedContract && (
        <div style={{
          width: "80%",
          maxWidth: "1000px",
          padding: "20px",
          backgroundColor: "#f9f9f9",
          borderRadius: "8px",
          marginTop: "20px",
          marginBottom: "20px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          alignSelf: "center",
          margin: "20px auto"
        }}>
          {loadingDetails ? (
            <p>Loading contract details...</p>
          ) : (
            <>
              <h2 style={{ color: "#0033a0" }}>{selectedContract.title}</h2>
              <p><strong>NAICS Code:</strong> {selectedContract.naics_code || "N/A"}</p>
              <p><strong>Response Deadline:</strong> {selectedContract.response_deadline || "N/A"}</p>
              <p><strong>Description:</strong> {selectedContract.description || "N/A"}</p>
              {selectedContract.link && (
                <p>
                  <strong>🔗 <a href={selectedContract.link} target="_blank" rel="noopener noreferrer">
                    View on SAM.gov
                  </a></strong>
                </p>
              )}
            </>
          )}
        </div>
      )}

      {selectedRfi && (
        <div style={{
          width: "80%",
          maxWidth: "1000px",
          padding: "20px",
          backgroundColor: "#fff8e6",
          borderRadius: "8px",
          marginTop: "20px",
          marginBottom: "20px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          margin: "20px auto",
          border: "1px solid #f0c36d"
        }}>
          {loadingDetails ? (
            <p>Loading RFI details...</p>
          ) : (
            <>
              <h2 style={{ color: "#b8860b" }}>{selectedRfi.title}</h2>
              <p><strong>Notice Type:</strong> {selectedRfi.notice_type || "RFI"}</p>
              <p><strong>Agency:</strong> {selectedRfi.agency || "N/A"}</p>
              <p><strong>NAICS Code:</strong> {selectedRfi.naics_code || "N/A"}</p>
              <p><strong>Response Deadline:</strong> {selectedRfi.response_deadline || "N/A"}</p>
              <p><strong>Description:</strong> {selectedRfi.description || "N/A"}</p>
              {selectedRfi.link && (
                <p>
                  <strong>🔗 <a href={selectedRfi.link} target="_blank" rel="noopener noreferrer">
                    View on SAM.gov
                  </a></strong>
                </p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
