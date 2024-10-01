import { type ConnectionSettings } from "src/permissions/PersonalizePage";
import { type AppInfo } from "./AppInfo";
import { type Connection } from "./Connection";

interface LoaderDataBase {
  connectionSettings: ConnectionSettings;
  permissionsEditable: boolean;
}

interface LoaderDataFromUrl extends LoaderDataBase {
  appInfo: AppInfo;
  oauthParams: {
    clientId: string;
    redirectUri: string;
  };
}

interface LoaderDataFromConnection extends LoaderDataBase {
  connection: Connection;
  appInfo?: AppInfo;
}

export const isLoaderDataFromUrl = (
  loaderData: PermissionPageLoaderData,
): loaderData is LoaderDataFromUrl => {
  return !!(loaderData as LoaderDataFromUrl).oauthParams;
};

export const isLoaderDataFromConnection = (
  loaderData: PermissionPageLoaderData,
): loaderData is LoaderDataFromConnection => {
  return !!(loaderData as LoaderDataFromConnection).connection;
};

export type PermissionPageLoaderData =
  | LoaderDataFromUrl
  | LoaderDataFromConnection;
