import styled from "@emotion/styled";
import { Button, Icon } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { Avatar } from "src/components/Avatar";
import { type AppInfo } from "src/types/AppInfo";
import {
  type Connection,
  ExpirationPeriod,
  type LimitFrequency,
  type PermissionState,
} from "src/types/Connection";
import { getAuth } from "src/utils/auth";
import { formatConnectionString } from "src/utils/formatConnectionString";
import { EditExpiration } from "./EditExpiration";
import { EditLimit } from "./EditLimit";
import { PermissionsEditableList } from "./PermissionsEditableList";
import { PermissionsList } from "./PermissionsList";

export interface ConnectionSettings {
  permissionStates: PermissionState[];
  amountInLowestDenom: number;
  limitFrequency: LimitFrequency;
  limitEnabled: boolean;
  expirationPeriod: ExpirationPeriod;
}

interface Props {
  appInfo?: AppInfo | undefined;
  connection?: Connection | undefined;
  connectionSettings: ConnectionSettings;
  updateConnectionSettings: (connectionSettings: ConnectionSettings) => void;
  onBack: () => void;
  onReset: () => void;
  permissionsEditable: boolean;
}

export const PersonalizePage = ({
  appInfo,
  connection,
  connectionSettings,
  updateConnectionSettings,
  onBack,
  onReset,
  permissionsEditable,
}: Props) => {
  const [isEditLimitVisible, setIsEditLimitVisible] = useState<boolean>(false);
  const [isEditExpirationVisible, setIsEditExpirationVisible] =
    useState<boolean>(false);
  const [internalConnectionSettings, setInternalConnectionSettings] =
    useState<ConnectionSettings>(connectionSettings);
  const auth = getAuth();
  const currency = auth.getCurrency();

  const isExistingConnection = !!connection;

  const handleEditLimit = () => {
    setIsEditLimitVisible(true);
  };

  const handleEditExpiration = () => {
    setIsEditExpirationVisible(true);
  };

  const handleSubmitEditLimit = ({
    amountInLowestDenom,
    frequency,
    enabled,
  }: {
    amountInLowestDenom: number;
    frequency: LimitFrequency;
    enabled: boolean;
  }) => {
    setInternalConnectionSettings({
      ...internalConnectionSettings,
      amountInLowestDenom,
      limitFrequency: frequency,
      limitEnabled: enabled,
    });
    setIsEditLimitVisible(false);
  };

  const handleSubmitEditExpiration = ({
    expirationPeriod,
  }: {
    expirationPeriod: ExpirationPeriod;
  }) => {
    setInternalConnectionSettings({
      ...internalConnectionSettings,
      expirationPeriod,
    });
    setIsEditExpirationVisible(false);
  };

  const handleUpdatePermissionStates = (
    permissionStates: PermissionState[],
  ) => {
    setInternalConnectionSettings({
      ...internalConnectionSettings,
      permissionStates,
    });
  };

  const handleSubmit = () => {
    updateConnectionSettings(internalConnectionSettings);
  };

  return (
    <Container>
      <PermissionsContainer>
        <PermissionsDescription>
          <AppSection>
            <Avatar src={appInfo?.avatar} size={48} />
            <AppDetails>
              <AppName>
                {appInfo && (
                  <>
                    <Title content={appInfo.name} />
                    {appInfo.nip05Verified && (
                      // TODO: Add NIP-68 verification status
                      <VerifiedBadge>
                        <Icon name="CheckmarkCircleTier3" width={20} />
                      </VerifiedBadge>
                    )}
                  </>
                )}
                {connection && <>{connection.name}</>}
              </AppName>
              {appInfo && <Body size="Large" content={appInfo.domain} />}
            </AppDetails>
          </AppSection>
          <Permissions>
            <Title content="Would like to" />
            {permissionsEditable ? (
              <PermissionsEditableList
                permissionStates={internalConnectionSettings.permissionStates}
                updatePermissionStates={handleUpdatePermissionStates}
              />
            ) : (
              <PermissionsList
                permissions={internalConnectionSettings.permissionStates
                  .filter((permissionState) => permissionState.enabled)
                  .map((permissionState) => permissionState.permission)}
              />
            )}
          </Permissions>
        </PermissionsDescription>
        <Limit onClick={handleEditLimit}>
          <Title
            content={
              internalConnectionSettings.limitEnabled
                ? `${formatConnectionString({ currency, limitFrequency: internalConnectionSettings.limitFrequency, amountInLowestDenom: internalConnectionSettings.amountInLowestDenom })} spending limit`
                : "No spending limit"
            }
          />
          <Icon name="Pencil" width={12} />
        </Limit>
        <Limit onClick={handleEditExpiration}>
          <Title
            content={
              internalConnectionSettings.expirationPeriod ===
              ExpirationPeriod.NONE
                ? "Connection never expires"
                : `Connection expires in 1 ${internalConnectionSettings.expirationPeriod.toLowerCase()}`
            }
          />
          <Icon name="Pencil" width={12} />
        </Limit>
      </PermissionsContainer>

      <ButtonSection>
        <Button
          text="Update permissions"
          kind={isExistingConnection ? "primary" : "tertiary"}
          paddingY="short"
          fullWidth
          onClick={handleSubmit}
        />
        <Button
          text="Reset"
          kind="secondary"
          paddingY="short"
          fullWidth
          onClick={onReset}
        />
      </ButtonSection>

      <EditLimit
        title="Spending limit"
        visible={isEditLimitVisible}
        amountInLowestDenom={internalConnectionSettings.amountInLowestDenom}
        currency={currency}
        frequency={internalConnectionSettings.limitFrequency}
        enabled={internalConnectionSettings.limitEnabled}
        handleSubmit={handleSubmitEditLimit}
        handleCancel={() => setIsEditLimitVisible(false)}
        isExistingConnection={isExistingConnection}
      />

      <EditExpiration
        title="Expiration date"
        visible={isEditExpirationVisible}
        expirationPeriod={internalConnectionSettings.expirationPeriod}
        handleSubmit={handleSubmitEditExpiration}
        handleCancel={() => setIsEditExpirationVisible(false)}
        isExistingConnection={isExistingConnection}
      />
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-self: center;
  gap: 24px;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;

  max-width: 345px;
`;

const PermissionsContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  border: 0.5px solid #c0c9d6;
  border-radius: 8px;
  background: ${colors.white};

  & > *:not(:last-child) {
    border-bottom: 0.5px solid #c0c9d6;
  }
`;

const PermissionsDescription = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.xl};
  width: 100%;
  padding: ${Spacing.px.lg};
`;

const AppSection = styled.div`
  display: flex;
  flex-direction: row;
  gap: 16px;
  align-items: center;
`;

const AppDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const AppName = styled.div`
  display: flex;
  flex-direction: row;
  gap: 4px;
`;

const VerifiedBadge = styled.div`
  color: #00d4ff;
  font-size: 12px;
`;

const Permissions = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.sm};
`;

const Limit = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 20px ${Spacing.px.lg};
  cursor: pointer;
`;

const ButtonSection = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 345px;
  width: 100%;
  gap: 16px;
`;
