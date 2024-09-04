import { useEffect, useState } from "react";
import { useAuth } from "src/utils/auth";

export const fetchUma = async () => {
  // const uma = await fetch(`${getBackendUrl()}/uma`, {
  //   method: "GET",
  //   cache: "force-cache",
  // }).then((res) => {
  //   if (res.ok) {
  //     return res.json() as Promise<{ uma: string }>;
  //   } else {
  //     throw new Error("Failed to fetch uma.");
  //   }
  // });
  const auth = useAuth();
  const response = { uma: auth.getUmaAddress() };
  return response.uma;
};

// TODO: Switch this to use the Auth state instead of fetching directly.
export function useUma() {
  const [uma, setUma] = useState<string>();
  const [error, setError] = useState<string>();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/require-await
    async function fetchUmaInternal() {
      setIsLoading(true);
      try {
        const uma = await fetchUma();
        if (!ignore) {
          setUma(uma);
          setIsLoading(false);
        }
      } catch (e: unknown) {
        const error = e as Error;
        setError(error.message);
        setIsLoading(false);
      }
    }

    let ignore = false;
    fetchUmaInternal();
    return () => {
      ignore = true;
    };
  }, []);

  return {
    uma,
    error,
    isLoading,
  };
}
