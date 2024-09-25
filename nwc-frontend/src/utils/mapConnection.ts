import dayjs from "dayjs";
import {
  type Connection,
  ConnectionStatus,
  PERMISSION_DESCRIPTIONS,
  type RawConnection,
} from "src/types/Connection";

const mapPermissions = (permissions: RawConnection["permissions"]) => {
  return permissions.map((permission) => ({
    type: permission.type,
    description: PERMISSION_DESCRIPTIONS[permission.type],
    optional: !!permission.optional,
  }));
};

const getStatus = (rawConnection: RawConnection): ConnectionStatus => {
  if (!rawConnection.expires_at) return ConnectionStatus.ACTIVE;
  return dayjs(rawConnection.expires_at).isAfter(dayjs())
    ? ConnectionStatus.ACTIVE
    : ConnectionStatus.INACTIVE;
};

export const mapConnection = (rawConnection: RawConnection): Connection => ({
  connectionId: rawConnection.connection_id,
  clientId: rawConnection.client_app?.client_id ?? "",
  name: rawConnection.name,
  createdAt: rawConnection.created_at,
  lastUsed: rawConnection.last_used_at,
  amountInLowestDenom: rawConnection.spending_limit?.limit_amount,
  amountInLowestDenomUsed: rawConnection.spending_limit?.amount_used,
  limitFrequency: rawConnection.spending_limit?.limit_frequency,
  limitEnabled: Boolean(rawConnection.spending_limit),
  currency: rawConnection.spending_limit
    ? {
        code: rawConnection.spending_limit.currency.code,
        symbol: rawConnection.spending_limit.currency.symbol,
        name: rawConnection.spending_limit.currency.name,
        decimals: rawConnection.spending_limit.currency.decimals,
      }
    : undefined,
  permissions: mapPermissions(rawConnection.permissions),
  avatar: rawConnection.client_app?.avatar,
  status: getStatus(rawConnection),
  expiresAt: rawConnection.expires_at,
});
