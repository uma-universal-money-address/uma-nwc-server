export const getBackendDomain = () => {
  if (typeof window !== "undefined") {
    return window.location.host;
  }
};
