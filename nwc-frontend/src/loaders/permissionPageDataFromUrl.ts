import { json, type LoaderFunction } from "react-router-dom";
import { fetchAppInfo } from "src/hooks/useAppInfo";
import {
  DEFAULT_CONNECTION_SETTINGS,
  PERMISSION_DESCRIPTIONS,
  type PermissionType,
} from "src/types/Connection";
import { type Currency } from "src/types/Currency";
import { type PermissionPageLoaderData } from "src/types/PermissionPageLoaderData";

export interface InitialPermissionsResponse {
  currencies: Currency[];
}

const getClientAppDefaultSettings = ({
  requiredCommands,
  optionalCommands,
  budget,
  expirationPeriod,
}: {
  requiredCommands: string;
  optionalCommands: string | undefined;
  budget: string | undefined;
  expirationPeriod: string | undefined;
}) => {
  const requiredPermissionStates =
    requiredCommands.length > 0
      ? requiredCommands.split(",").map((command) => ({
          permission: {
            type: command.toLowerCase() as PermissionType,
            description: PERMISSION_DESCRIPTIONS[command.toLowerCase()],
            optional: false,
          },
          enabled: true,
        }))
      : [];
  const optionalPermissionStates =
    optionalCommands && optionalCommands.length > 0
      ? optionalCommands.split(",").map((command) => ({
          permission: {
            type: command.toLowerCase() as PermissionType,
            description: PERMISSION_DESCRIPTIONS[command.toLowerCase()],
            optional: true,
          },
          enabled: false,
        }))
      : [];
  const permissionStates = requiredPermissionStates.concat(
    optionalPermissionStates,
  );
  const amountCurrency = budget?.split("/")[0];
  let limitFrequency = budget?.split("/")[1];
  const amountParts = amountCurrency?.split(".") ?? [undefined, undefined];
  const currencyCode = amountParts[1] ?? "SAT";
  let amountInLowestDenom = !!amountParts[0]
    ? parseInt(amountParts[0], 10)
    : undefined;

  if (permissionStates.length === 0) {
    permissionStates.concat(DEFAULT_CONNECTION_SETTINGS.permissionStates);
  }

  if (!amountInLowestDenom) {
    amountInLowestDenom = DEFAULT_CONNECTION_SETTINGS.amountInLowestDenom;
  }

  if (!limitFrequency) {
    limitFrequency = DEFAULT_CONNECTION_SETTINGS.limitFrequency;
  }

  if (!expirationPeriod) {
    expirationPeriod = DEFAULT_CONNECTION_SETTINGS.expirationPeriod;
  }

  return {
    permissionStates,
    amountInLowestDenom,
    limitFrequency,
    limitEnabled: DEFAULT_CONNECTION_SETTINGS.limitEnabled,
    expirationPeriod,
    currencyCode,
  };
};

export const permissionsPageDataFromUrl = (async ({ request }) => {
  const url = new URL(request.url);
  const params = url.searchParams;
  const oauthParams = {
    clientId: params.get("client_id"),
    redirectUri: params.get("redirect_uri"),
    responseType: params.get("response_type"),
    codeChallenge: params.get("code_challenge"),
    codeChallengeMethod: params.get("code_challenge_method"),
  };
  const nwcParams = {
    requiredCommands: params.get("required_commands") || "",
    optionalCommands: params.get("optional_commands") || undefined,
    budget: params.get("budget") || undefined,
    expirationPeriod: params.get("expiration_period") || undefined,
  };

  if (
    !oauthParams.clientId ||
    !oauthParams.redirectUri ||
    !oauthParams.responseType ||
    !oauthParams.codeChallenge ||
    !oauthParams.codeChallengeMethod
  ) {
    throw new Response("Invalid OAuth parameters", { status: 400 });
  }

  const appInfo = await fetchAppInfo(oauthParams.clientId);

  return json(
    {
      appInfo,
      connectionSettings: getClientAppDefaultSettings(nwcParams),
      oauthParams,
    } as PermissionPageLoaderData,
    { status: 200 },
  );
}) satisfies LoaderFunction;
