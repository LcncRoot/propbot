import { useState, useEffect } from "react";

function App() {
  const [grants, setGrants] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [searchQuery, setSearchQuery] = useState(""); // Only trigger search on button press

  // Function to fetch search results from backend
  const fetchSearchResults = (query) => {
    console.log(`🔍 Fetching grants with query: "${query}"`);

    if (!query.trim()) {
      console.log("🟢 Fetching ALL grants (empty search)");
      fetch("http://127.0.0.1:8000/grants")
        .then((res) => res.json())
        .then((data) => {
          console.log("✅ Grants received:", data);
          setGrants(data.grants);
        })
        .catch((error) => console.error("❌ Error fetching grants:", error));
    } else {
      console.log(`🟢 Searching for "${query}"`);
      fetch(`http://127.0.0.1:8000/search?query=${encodeURIComponent(query)}`)
        .then((res) => res.json())
        .then((data) => {
          console.log("✅ Search results received:", data);
          setGrants(data.matches);
        })
        .catch((error) => console.error("❌ Error searching grants:", error));
    }
  };

  // Fetch grants when user presses search
  useEffect(() => {
    if (searchQuery !== "") {
      fetchSearchResults(searchQuery);
    }
  }, [searchQuery]);

  // Handle Enter keypress
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      setSearchQuery(searchTerm);
    }
  };

  return (
    <div className="container">
      <h1>PropBot - Grant Search</h1>
      <input
        type="text"
        placeholder="Search grants..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onKeyDown={handleKeyDown} // Listen for Enter key
      />
      <button onClick={() => setSearchQuery(searchTerm)}>Search</button> {/* Search button */}
      <ul>
        {grants.length > 0 ? (
          grants.map((grant, index) => (
            <li key={index}>
              <h3>{grant.title}</h3>
              <p><strong>Opportunity ID:</strong> {grant.opportunity_id}</p> {/* ✅ Now displays opportunity_id */}
              <p><strong>Agency:</strong> {grant.agency}</p>
              <p><strong>Funding Amount:</strong> ${grant.funding_amount}</p>
              <p><strong>Deadline:</strong> {grant.deadline}</p>
              {grant.grant_url && <a href={grant.grant_url} target="_blank">View Details</a>}
            </li>
          ))
        ) : (
          <p>No grants found.</p>
        )}
      </ul>
    </div>
  );
}

export default App;
