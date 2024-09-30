import dayjs from "dayjs";
import {
  type Connection,
  ConnectionStatus,
  type Permission,
  PERMISSION_DESCRIPTIONS,
  type RawConnection,
} from "src/types/Connection";

const mapPermissions = (
  permissions: RawConnection["permissions"],
): Permission[] => {
  return permissions.map((permission) => ({
    type: permission,
    description: PERMISSION_DESCRIPTIONS[permission],
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
  budgetCurrency: {
    code: rawConnection.budget_currency.code,
    symbol: rawConnection.budget_currency.symbol,
    name: rawConnection.budget_currency.name,
    decimals: rawConnection.budget_currency.decimals,
  },
  permissions: mapPermissions(rawConnection.permissions),
  avatar: rawConnection.client_app?.avatar,
  status: getStatus(rawConnection),
  expiresAt: rawConnection.expires_at,
});
