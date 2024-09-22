import { json, type LoaderFunction } from "react-router-dom";
import { fetchAppInfo } from "src/hooks/useAppInfo";
import {
  type Connection,
  DEFAULT_CONNECTION_SETTINGS,
} from "src/types/Connection";
import { type Currency } from "src/types/Currency";
import { type PermissionPageLoaderData } from "src/types/PermissionPageLoaderData";
import { getBackendUrl } from "src/utils/backendUrl";
import { fetchWithAuth } from "src/utils/fetchWithAuth";
import { mapConnection } from "src/utils/mapConnection";

export interface InitialPermissionsResponse {
  currencies: Currency[];
}

const getConnectionSettings = (connection: Connection) => {
  const permissionStates = connection.permissions.map((permission) => ({
    permission,
    enabled: true,
  }));

  return {
    permissionStates,
    amountInLowestDenom: connection.amountInLowestDenom,
    limitFrequency: connection.limitFrequency,
    limitEnabled: connection.limitEnabled,
    expirationPeriod: DEFAULT_CONNECTION_SETTINGS.expirationPeriod,
  };
};

export const permissionsPageData = (async ({ params }) => {
  let connection: Connection | undefined;
  try {
    const response = await fetchWithAuth(
      `${getBackendUrl()}/api/connection/${params.connectionId}`,
    );
    const rawConnection = await response.json();
    connection = mapConnection(rawConnection);
  } catch (e) {
    console.error(e);
  }

  if (!connection) {
    throw new Response("Connection not found", { status: 404 });
  }

  const appInfo = await fetchAppInfo(connection.clientId);

  return json(
    {
      appInfo,
      connectionSettings: getConnectionSettings(connection),
      connection,
    } as PermissionPageLoaderData,
    { status: 200 },
  );
}) satisfies LoaderFunction;
