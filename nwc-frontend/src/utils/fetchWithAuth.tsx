import { getAuth } from "./auth";

export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const auth = getAuth();
  const token = auth.getAuthToken();

  if (!token) {
    throw new Error("Unable to fetch without auth token");
  }

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });
};
