import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { UIKit } from "./pages/UIKit";
import { Dashboard } from "./pages/Dashboard";
import "./styles/globals.css";

// Simple routing based on query params
const params = new URLSearchParams(window.location.search);
const showUIKit = params.has('ui-kit');
const showLegacy = params.has('legacy');

function Router() {
  if (showUIKit) return <UIKit />;
  if (showLegacy) return <App />;
  return <Dashboard />;  // Dashboard is now the default
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Router />
  </React.StrictMode>
);
