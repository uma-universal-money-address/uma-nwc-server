import { getBackendDomain } from "./backendDomain";
import isDevelopment from "./isDevelopment";

export const getBackendUrl = () => {
  const backendDomain = getBackendDomain();
  return isDevelopment || isDomainLocalhost(backendDomain)
    ? `http://${backendDomain}`
    : `https://${backendDomain}`;
};

const isDomainLocalhost = (domain: string) => {
  const domainWithoutPort = domain.split(":")[0];
  const tld = domainWithoutPort.split(".").pop();
  return (
    domainWithoutPort === "localhost" ||
    domainWithoutPort === "127.0.0.1" ||
    tld === "local" ||
    tld === "internal"
  );
};
