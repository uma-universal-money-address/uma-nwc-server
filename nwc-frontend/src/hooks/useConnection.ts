import { useEffect, useState } from "react";
import {
  type Connection,
  type ConnectionStatus,
  type InitialConnection,
  type LimitFrequency,
  type RawConnection,
} from "src/types/Connection";
import { getBackendUrl } from "src/utils/backendUrl";
import { fetchWithAuth } from "src/utils/fetchWithAuth";
import { mapConnection } from "src/utils/mapConnection";

export const useConnection = ({ connectionId }: { connectionId: string }) => {
  const [connection, setConnection] = useState<Connection>();
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>();

  useEffect(() => {
    async function fetchConnection() {
      if (!connectionId) {
        setConnection(undefined);
        return;
      }
      setIsLoading(true);
      try {
        const response = await fetchWithAuth(
          `${getBackendUrl()}/api/connection/${connectionId}`,
        );
        const rawConnection = await response.json();
        const connection = mapConnection(rawConnection);
        setConnection(connection);
      } catch (e) {
        const error = e as Error;
        console.error(error);
        setError(error.message);
      }

      setIsLoading(false);
    }

    fetchConnection();
  }, [connectionId]);

  const updateConnection = async ({
    amountInLowestDenom,
    limitFrequency,
    limitEnabled,
    status,
  }: {
    amountInLowestDenom?: number | undefined;
    limitFrequency?: LimitFrequency | undefined;
    limitEnabled: boolean;
    status: ConnectionStatus;
  }) => {
    try {
      const response = await fetchWithAuth(
        `${getBackendUrl()}/api/connection/${connectionId}`,
        {
          method: "POST",
          body: JSON.stringify({
            amountInLowestDenom,
            limitFrequency,
            limitEnabled,
            status,
          }),
        },
      );
      const result = await response.json();
      if (result.success) {
        return true;
      }
      const updatedConnection = mapConnection(result as RawConnection);
      setConnection(updatedConnection);
      return true;
    } catch (e) {
      const error = e as Error;
      console.error(error);
      setError(error.message);
      return false;
    }
  };

  return {
    connection,
    isLoading,
    updateConnection,
    error,
  };
};

export const updateConnection = async ({
  connectionId,
  amountInLowestDenom,
  limitFrequency,
  limitEnabled,
  expiration,
  status,
}: {
  connectionId: string;
  amountInLowestDenom?: number | undefined;
  limitFrequency?: LimitFrequency | undefined;
  limitEnabled: boolean;
  expiration?: string | undefined;
  status: ConnectionStatus;
}) => {
  try {
    await fetchWithAuth(`${getBackendUrl()}/api/connection/${connectionId}`, {
      method: "POST",
      body: JSON.stringify({
        amountInLowestDenom,
        limitFrequency,
        limitEnabled,
        expiration,
        status,
      }),
    });
    return true;
  } catch (e) {
    return { error: e };
  }
};

export const initializeConnection = async (
  initialConnection: InitialConnection,
) => {
  try {
    const response = await fetchWithAuth(`${getBackendUrl()}/api/app`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({ ...initialConnection }),
    });
    if (!response.ok) {
      return { error: response.statusText };
    }
    return response.json();
  } catch (e) {
    return { error: e };
  }
};

export const initializeManualConnection = async (
  initialConnection: InitialConnection,
) => {
  try {
    const response = await fetchWithAuth(
      `${getBackendUrl()}/api/connection/manual`,
      {
        method: "POST",
        headers: {
          "content-type": "application/json",
        },
        body: JSON.stringify({ ...initialConnection }),
      },
    );
    if (!response.ok) {
      return { error: response.statusText };
    }
    console.log("Connection initialized", initialConnection);
    return response.json();
  } catch (e) {
    return { error: e };
  }
};
