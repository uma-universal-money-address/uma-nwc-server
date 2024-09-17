import { ConnectionSettings } from "src/permissions/PersonalizePage";
import { AppInfo } from "./AppInfo";
import { Connection } from "./Connection";
import { Currency } from "./Currency";

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
