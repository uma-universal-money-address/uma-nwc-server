import { useEffect, useState } from "react";
import {
  Connection,
  ConnectionStatus,
  InitialConnection,
  LimitFrequency,
} from "src/types/Connection";
import { getBackendUrl } from "src/utils/backendUrl";
import { fetchWithAuth } from "src/utils/fetchWithAuth";
import { mapConnection } from "src/utils/mapConnection";

export const useConnection = ({ connectionId }: { connectionId: string }) => {
  const [connection, setConnection] = useState<Connection>();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchConnection() {
      setIsLoading(true);
      try {
        const response = await fetchWithAuth(
          `${getBackendUrl()}/api/connection/${connectionId}`,
        );
        const rawConnection = await response.json();
        const connection = mapConnection(rawConnection);
        setConnection(connection);
      } catch (e) {
        console.error(e);
      }

      setIsLoading(false);
    }

    let ignore = false;
    fetchConnection();
    return () => {
      ignore = true;
    };
  }, [connectionId]);

  // eslint-disable-next-line @typescript-eslint/require-await
  const updateConnection = async ({
    amountInLowestDenom,
    limitFrequency,
    limitEnabled,
    status,
  }: {
    amountInLowestDenom: number;
    limitFrequency: LimitFrequency;
    limitEnabled: boolean;
    status: ConnectionStatus;
  }) => {
    try {
      // const response = await fetch("/connection", {
      //   method: "POST",
      //   body: JSON.stringify({ connectionId: connection.connectionId, amountInLowestDenom, limitFrequency, limitEnabled, status }),
      // });
      setConnection({
        ...connection,
        amountInLowestDenom,
        limitFrequency,
        limitEnabled,
        status,
      });
      return true;
    } catch (e) {
      console.error(e);
      return false;
    }
  };

  return {
    connection,
    isLoading,
    updateConnection,
  };
};

// eslint-disable-next-line @typescript-eslint/require-await
export const updateConnection = async ({
  connectionId,
  amountInLowestDenom,
  limitFrequency,
  limitEnabled,
  expiration,
  status,
}: {
  connectionId: string;
  amountInLowestDenom: number;
  limitFrequency: LimitFrequency;
  limitEnabled: boolean;
  expiration: string;
  status: ConnectionStatus;
}) => {
  try {
    // const response = await fetch("/connection", {
    //   method: "POST",
    //   body: JSON.stringify({ connectionId: connectionId, amountInLowestDenom, limitFrequency, limitEnabled, expiration, status }),
    // });
    return true;
  } catch (e) {
    return { error: e };
  }
};

// eslint-disable-next-line @typescript-eslint/require-await
export const initializeConnection = async (
  initialConnection: InitialConnection,
) => {
  try {
    const response = await fetch("/apps/new", {
      method: "POST",
      body: JSON.stringify({ ...initialConnection }),
    });
    console.log("Connection initialized", response);
    if (!response.ok) {
      return { error: response.statusText };
    }
    return response.json();
  } catch (e) {
    return { error: e };
  }
};

// eslint-disable-next-line @typescript-eslint/require-await
export const initializeManualConnection = async (
  initialConnection: InitialConnection,
) => {
  try {
    const response = await fetch("api/connections/manual", {
      method: "POST",
      body: JSON.stringify({ ...initialConnection }),
    });
    if (!response.ok) {
      return { error: response.statusText };
    }
    console.log("Connection initialized", initialConnection);
    return response.json();
  } catch (e) {
    return { error: e };
  }
};
