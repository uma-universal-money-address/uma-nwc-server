import { useEffect, useState } from "react";
import { type Connection } from "src/types/Connection";
import { fetchConnections } from "src/utils/fetchConnections";

export function useConnections() {
  const [connections, setConnections] = useState<Connection[]>();
  const [error, setError] = useState<string>();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchConnectionsInternal() {
      setIsLoading(true);
      try {
        const response = await fetchConnections();
        if (!ignore) {
          setConnections(response);
          setIsLoading(false);
        }
      } catch (e: unknown) {
        const error = e as Error;
        setError(error.message);
        setIsLoading(false);
      }
    }

    let ignore = false;
    fetchConnectionsInternal();
    return () => {
      ignore = true;
    };
  }, []);

  return {
    connections,
    error,
    isLoading,
  };
}
