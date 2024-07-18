import React from "react";
import ReactDOM from "react-dom/client";
import ConnectionPage from "./connections/ConnectionPage";
import GlobalNotificationContext from "./hooks/useGlobalNotificationContext";
import { Root } from "./Root";


ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
);
