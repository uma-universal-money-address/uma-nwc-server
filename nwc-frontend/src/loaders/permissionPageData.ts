import { json, LoaderFunction } from "react-router-dom";
import { fetchAppInfo } from "src/hooks/useAppInfo";
import { Connection, DEFAULT_CONNECTION_SETTINGS } from "src/types/Connection";
import { PermissionPageLoaderData } from "src/types/PermissionPageLoaderData";
import { MOCKED_CONNECTIONS } from "src/utils/fetchConnections";

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
  // const response = await fetch(`/connection/${params.connectionId}`);
  // const connection = await response.json();
  const connection = MOCKED_CONNECTIONS.find(
    (c) => c.connectionId === params.connectionId,
  );

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
