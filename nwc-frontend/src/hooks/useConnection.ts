import { useEffect, useState } from "react";
import {
  Connection,
  ConnectionStatus,
  InitialConnection,
  LimitFrequency,
} from "src/types/Connection";
import { MOCKED_CONNECTIONS } from "src/utils/fetchConnections";

export const useConnection = ({ connectionId }: { connectionId: string }) => {
  const [connection, setConnection] = useState<Connection>();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/require-await
    async function fetchConnection() {
      try {
        // const response = await fetch(`/connection/${connectionId}`);
        // const connection = await response.json();
        setIsLoading(true);
        const connection = MOCKED_CONNECTIONS.find(
          (c) => c.connectionId === connectionId,
        );
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
        disconnectedAt:
          status === ConnectionStatus.INACTIVE
            ? undefined
            : new Date().toISOString(),
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
    // const response = await fetch("/manual-connection", {
    //   method: "POST",
    //   body: JSON.stringify({ ...initialConnection, }),
    // });
    console.log("Connection initialized", initialConnection);
    return {
      connectionId: "1",
      pairingUri:
        "nostr+walletconnect://test_id?relay=wss://relay.getalby.com/v1&secret=test_secret&lud16=$test@uma.me",
    };
  } catch (e) {
    return { error: e };
  }
};
