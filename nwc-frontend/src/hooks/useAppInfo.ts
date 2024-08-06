import { useEffect, useState } from "react";
import { AppInfo } from "src/types/AppInfo";

export const useAppInfo = ({ clientId }: { clientId: string }) => {
  const [appInfo, setAppInfo] = useState<AppInfo>();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/require-await
    async function fetchAppInfo() {
      try {
        // const response = await fetch("/app");
        // const appInfo = await response.json();
        setIsLoading(true);
        const appInfo = {
          clientId,
          name: "Cool App",
          verified: true,
          domain: "coolapp.com",
          avatar: "/default-app-logo.svg",
        };
        setAppInfo(appInfo);
      } catch (e) {
        console.error(e);
      }

      setIsLoading(false);
    }

    let ignore = false;
    fetchAppInfo();
    return () => {
      ignore = true;
    };
  }, [clientId]);

  return {
    appInfo,
    isLoading,
  };
};
