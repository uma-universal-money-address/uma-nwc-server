import { json, LoaderFunction } from "react-router-dom";
import { fetchAppInfo } from "src/hooks/useAppInfo";
import { fetchUma } from "src/hooks/useUma";
import {
  DEFAULT_CONNECTION_SETTINGS,
  PERMISSION_DESCRIPTIONS,
  PermissionType,
} from "src/types/Connection";
import { PermissionPageLoaderData } from "src/types/PermissionPageLoaderData";

export interface InitialPermissionsResponse {
  defaultCurrency: Currency;
  currencies: Currency[];
}

const getClientAppDefaultSettings = ({
  requiredCommands,
  optionalCommands,
  budget,
  expirationPeriod,
}) => {
  const requiredPermissionStates = requiredCommands
    .split(",")
    .map((command) => ({
      permission: {
        type: command.toUpperCase() as PermissionType,
        description: PERMISSION_DESCRIPTIONS[command.toLowerCase()],
        optional: false,
      },
      enabled: true,
    }));
  const optionalPermissionStates = optionalCommands
    .split(",")
    .map((command) => ({
      permission: {
        type: command.toUpperCase() as PermissionType,
        description: PERMISSION_DESCRIPTIONS[command.toLowerCase()],
        optional: true,
      },
      enabled: false,
    }));
  const permissionStates = requiredPermissionStates.concat(
    optionalPermissionStates,
  );
  let [amountCurrency, limitFrequency] = budget
    ? budget.split("/")
    : [undefined, undefined];
  let [amountInLowestDenom, currencyCode] = amountCurrency
    ? amountCurrency.split(".")
    : [undefined, undefined];

  if (permissionStates.length === 0) {
    permissionStates.concat(DEFAULT_CONNECTION_SETTINGS.permissionStates);
  }

  if (!amountInLowestDenom) {
    amountInLowestDenom = DEFAULT_CONNECTION_SETTINGS.amountInLowestDenom;
  }

  if (!currencyCode) {
    currencyCode = "SAT";
  }

  if (!limitFrequency) {
    limitFrequency = DEFAULT_CONNECTION_SETTINGS.limitFrequency;
  }

  if (!expirationPeriod) {
    expirationPeriod = DEFAULT_CONNECTION_SETTINGS.expirationPeriod;
  }

  // TODO: perform rough currency conversion to user's home currency

  return {
    permissionStates,
    amountInLowestDenom,
    limitFrequency,
    limitEnabled: DEFAULT_CONNECTION_SETTINGS.limitEnabled,
    expirationPeriod,
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
    optionalCommands: params.get("optional_commands") || "",
    budget: params.get("budget"),
    expirationPeriod: params.get("expiration_period"),
  };

  // const { defaultCurrency } =  await fetch(
  //   "/user/currencies",
  //   {
  //     method: "GET",
  //   },
  // );

  const defaultCurrency = {
    code: "USD",
    name: "United States Dollar",
    symbol: "$",
    decimals: 2,
    type: "fiat",
  };

  const [appInfo, uma] = await Promise.all([
    fetchAppInfo(oauthParams.clientId),
    fetchUma(),
  ]);

  return json(
    {
      appInfo,
      uma,
      connectionSettings: getClientAppDefaultSettings(nwcParams),
      defaultCurrency,
      oauthParams,
    } as PermissionPageLoaderData,
    { status: 200 },
  );
}) satisfies LoaderFunction;
