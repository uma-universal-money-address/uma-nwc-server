import { type RawConnection } from "src/types/Connection";
import { getBackendUrl } from "./backendUrl";
import { fetchWithAuth } from "./fetchWithAuth";
import { mapConnection } from "./mapConnection";

export const fetchConnections = async () => {
  const rawConnections = await fetchWithAuth(
    `${getBackendUrl()}/api/connections`,
    {
      method: "GET",
    },
  ).then((res) => {
    if (res.ok) {
      return res.json() as Promise<RawConnection[]>;
    } else {
      throw new Error("Failed to fetch connections.");
    }
  });

  return rawConnections.map(mapConnection);
};
