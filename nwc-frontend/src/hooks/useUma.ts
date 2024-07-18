import { useEffect, useState } from "react";

export function useUma() {
  const [uma, setUma] = useState<string>();
  const [error, setError] = useState<string>();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/require-await
    async function fetchUma() {
      setIsLoading(true);
      try {
        // const response = await fetch(`${getBackendUrl()}/uma`, {
        //   method: "GET",
        //   cache: "force-cache",
        // }).then((res) => {
        //   if (res.ok) {
        //     return res.json() as Promise<{ uma: string }>;
        //   } else {
        //     throw new Error("Failed to fetch uma.");
        //   }
        // });
        const response = { uma: "$test@vasp.com" };
        if (!ignore) {
          setUma(response.uma);
          setIsLoading(false);
        }
      } catch (e: unknown) {
        const error = e as Error;
        setError(error.message);
        setIsLoading(false);
      }
    }

    let ignore = false;
    fetchUma();
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
