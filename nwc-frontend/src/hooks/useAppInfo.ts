import { useEffect, useState } from "react";
import { type AppInfo } from "src/types/AppInfo";
import { getBackendUrl } from "src/utils/backendUrl";
import { fetchWithAuth } from "src/utils/fetchWithAuth";

export const fetchAppInfo = async (clientId: string) => {
  const response = await fetchWithAuth(
    `${getBackendUrl()}/api/app?clientId=${clientId}`,
  );
  const appInfo = await response.json();
  return {
    clientId: appInfo.clientId,
    name: appInfo.name,
    nip05Verified: appInfo.nip05Verification == "VERIFIED",
    nip68Verification: appInfo.nip68Verification,
    domain: appInfo.domain,
    avatar: appInfo.avatar,
  };
};

export const useAppInfo = ({ clientId }: { clientId?: string | undefined }) => {
  const [appInfo, setAppInfo] = useState<AppInfo>();
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    async function fetchAppInfoInternal(clientId: string) {
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
    if (clientId) {
      fetchAppInfoInternal(clientId);
    }
    return () => {
      ignore = true;
    };
  }, [clientId]);

  return {
    appInfo,
    isLoading,
  };
};
