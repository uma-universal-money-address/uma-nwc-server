import { getBackendDomain } from "./backendDomain";
import isDevelopment from "./isDevelopment";

export const getBackendUrl = () => {
  const backendDomain = getBackendDomain();
  return isDevelopment ? `http://${backendDomain}` : `https://${backendDomain}`;
};
