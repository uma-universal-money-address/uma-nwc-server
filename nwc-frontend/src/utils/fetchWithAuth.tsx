import { getAuth } from "./auth";

export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const auth = getAuth();
  const token = auth.getAuthToken();

  if (!auth.isLoggedIn()) {
    auth.redirectToLogin();
  }

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });
};
