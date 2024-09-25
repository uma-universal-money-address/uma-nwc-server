import { useEffect, useState } from "react";
import { type AppInfo } from "src/types/AppInfo";
import { fetchWithAuth } from "src/utils/fetchWithAuth";

export const fetchAppInfo = async (clientId: string) => {
  const response = await fetchWithAuth(`/api/app?clientId=${clientId}`);
  const appInfo = await response.json();
  return {
    clientId: appInfo.clientId,
    name: appInfo.name,
    verified: appInfo.verified === "VERIFIED",
    domain: appInfo.domain,
    avatar: appInfo.avatar,
  };
};

export const useAppInfo = ({ clientId }: { clientId: string }) => {
  const [appInfo, setAppInfo] = useState<AppInfo>();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
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
