import assert from "assert";
import isDevelopment from "./isDevelopment";

export const getBackendDomain = () => {
  if (typeof window !== "undefined") {
    return window.location.host;
  }
};
