import "./init.js"; // import first!
import { RelayEnvironmentProvider } from "react-relay";
import { ScreenSizeProvider } from "./context/screenSize-context";
import environment from "./relayEnvironment";
import React from "react";
import ReactDOM from "react-dom/client";
import Router from "./components/Router";
import "./assets/scss/theme.scss";
import "react-image-lightbox/style.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <RelayEnvironmentProvider environment={environment}>
    <ScreenSizeProvider>
      <React.StrictMode>
        <div className="App h-100" data-testid="mainApp">
          <Router />
        </div>
      </React.StrictMode>
    </ScreenSizeProvider>
  </RelayEnvironmentProvider>
);
