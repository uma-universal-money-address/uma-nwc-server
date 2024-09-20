import { type ConnectionSettings } from "src/permissions/PersonalizePage";
import { type AppInfo } from "./AppInfo";
import { type Connection } from "./Connection";

interface LoaderDataBase {
  appInfo: AppInfo;
  connectionSettings: ConnectionSettings;
}

interface LoaderDataFromUrl extends LoaderDataBase {
  oauthParams: {
    clientId: string;
    redirectUri: string;
    responseType: string;
    codeChallenge: string;
    codeChallengeMethod: string;
  };
}

interface LoaderDataFromConnection extends LoaderDataBase {
  connection: Connection;
}

export type PermissionPageLoaderData =
  | LoaderDataFromUrl
  | LoaderDataFromConnection;
