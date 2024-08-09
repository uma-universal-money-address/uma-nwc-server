import { useEffect, useState } from "react";
import { AppInfo } from "src/types/AppInfo";

export const fetchAppInfo = async (clientId: string) => {
  // const response = await fetch("/app", { method: "GET", body: JSON.stringify({ clientId }) });
  // const appInfo = await response.json();
  const appInfo = {
    clientId,
    name: "Cool App",
    verified: true,
    domain: "coolapp.com",
    avatar: "/default-app-logo.svg",
  };
  return appInfo;
};

export const useAppInfo = ({ clientId }: { clientId: string }) => {
  const [appInfo, setAppInfo] = useState<AppInfo>();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/require-await
    async function fetchAppInfoInternal() {
      setIsLoading(true);
      try {
        const appInfo = await fetchAppInfo(clientId);
        if (!ignore) {
          setAppInfo(appInfo);
        }
      } catch (e) {
        console.error(e);
      }

      setIsLoading(false);
    }

    let ignore = false;

    fetchAppInfoInternal();
    return () => {
      ignore = true;
    };
  }, [clientId]);

  return {
    appInfo,
    isLoading,
  };
};
