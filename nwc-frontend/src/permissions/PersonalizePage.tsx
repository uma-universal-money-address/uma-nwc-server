import styled from "@emotion/styled";
import { Button, Icon } from "@lightsparkdev/ui/components";
import { Label } from "@lightsparkdev/ui/components/typography/Label";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";
import { Avatar } from "src/components/Avatar";
import {
  Connection,
  ExpirationPeriod,
  LimitFrequency,
  PermissionState,
} from "src/types/Connection";
import { formatConnectionString } from "src/utils/formatConnectionString";
import { EditLimit } from "./EditLimit";
import { PermissionsEditableList } from "./PermissionsEditableList";

export interface ConnectionSettings {
  permissionStates: PermissionState[];
  amountInLowestDenom: number;
  limitFrequency: LimitFrequency;
  limitEnabled: boolean;
  expirationPeriod: ExpirationPeriod;
}

interface Props {
  connection: Connection;
  connectionSettings: ConnectionSettings;
  updateConnectionSettings: (connectionSettings: ConnectionSettings) => void;
  onBack: () => void;
  onReset: () => void;
}

export const PersonalizePage = ({
  connection,
  connectionSettings,
  updateConnectionSettings,
  onBack,
  onReset,
}: Props) => {
  const [isEditLimitVisible, setIsEditLimitVisible] = useState<boolean>(false);
  const [internalConnectionSettings, setInternalConnectionSettings] =
    useState<ConnectionSettings>(connectionSettings);

  const { name, domain, avatar, currency, verified } = connection;

  const handleEdit = () => {
    setIsEditLimitVisible(true);
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
            <Avatar src={avatar} size={48} />
            <AppDetails>
              <AppName>
                {name}
                {verified ? (
                  <VerifiedBadge>
                    <Icon name="CheckmarkCircleTier3" width={20} />
                  </VerifiedBadge>
                ) : null}
              </AppName>
              <AppDomain>{domain}</AppDomain>
            </AppDetails>
          </AppSection>
          <Permissions>
            <Label size="Large" content="Would like to" />
            <PermissionsEditableList
              permissionStates={internalConnectionSettings.permissionStates}
              updatePermissionStates={handleUpdatePermissionStates}
            />
          </Permissions>
        </PermissionsDescription>
        <Limit onClick={handleEdit}>
          <LimitDescription>
            {internalConnectionSettings.limitEnabled
              ? `${formatConnectionString({ currency, limitFrequency: internalConnectionSettings.limitFrequency, amountInLowestDenom: internalConnectionSettings.amountInLowestDenom })} spending limit`
              : "No spending limit"}
          </LimitDescription>
          <Icon name="Pencil" width={12} />
        </Limit>
      </PermissionsContainer>

      <ButtonSection>
        <Button
          text="Update permissions"
          kind="primary"
          fullWidth
          onClick={handleSubmit}
        />
        <Button text="Reset" kind="secondary" fullWidth onClick={onReset} />
      </ButtonSection>

      <EditLimit
        title="Spending limit"
        visible={isEditLimitVisible}
        amountInLowestDenom={internalConnectionSettings.amountInLowestDenom}
        currency={currency}
        limitFrequency={internalConnectionSettings.limitFrequency}
        frequency={internalConnectionSettings.limitFrequency}
        enabled={internalConnectionSettings.limitEnabled}
        handleSubmit={handleSubmitEditLimit}
        handleCancel={() => setIsEditLimitVisible(false)}
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
`;

const PermissionsDescription = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.xl};
  width: 100%;
  border-bottom: 0.5px solid #c0c9d6;
  padding: ${Spacing.lg};
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
  gap: 4px;
`;

const AppName = styled.div`
  display: flex;
  flex-direction: row;
  gap: 4px;
`;

const AppDomain = styled.div`
  color: #686a72;
  font-size: 14px;
`;

const VerifiedBadge = styled.div`
  color: #00d4ff;
  font-size: 12px;
`;

const Permissions = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.sm};
`;

const Limit = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: ${Spacing.lg};
  cursor: pointer;
`;

const LimitDescription = styled.div`
  color: #686a72;
  font-size: 16px;
`;

const ButtonSection = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 345px;
  width: 100%;
  gap: 16px;
`;
