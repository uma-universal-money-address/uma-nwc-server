import styled from "@emotion/styled";
import { Button, Icon, TextInput } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Headline } from "@lightsparkdev/ui/components/typography/Headline";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import dayjs, { type ManipulateType } from "dayjs";
import { useState } from "react";
import { initializeManualConnection } from "src/hooks/useConnection";
import { useGlobalNotificationContext } from "src/hooks/useGlobalNotificationContext";
import { EditExpiration } from "src/permissions/EditExpiration";
import { EditLimit } from "src/permissions/EditLimit";
import { PermissionsEditableList } from "src/permissions/PermissionsEditableList";
import { type ConnectionSettings } from "src/permissions/PersonalizePage";
import {
  DEFAULT_CONNECTION_SETTINGS,
  ExpirationPeriod,
  type LimitFrequency,
  type PermissionState,
} from "src/types/Connection";
import { getAuth } from "src/utils/auth";
import { formatConnectionString } from "src/utils/formatConnectionString";
import { Routes, generatePath } from "../routes/Routes";
import { ManualConnectionHowItWorksModal } from "./ManualConnectionHowItWorksModal";
import { PendingConnectionPage } from "./PendingConnectionPage";

export default function ManualConnectionPage() {
  const [isHowItWorksVisible, setIsHowItWorksVisible] =
    useState<boolean>(false);
  const [isEditLimitVisible, setIsEditLimitVisible] = useState<boolean>(false);
  const [isEditExpirationVisible, setIsEditExpirationVisible] =
    useState<boolean>(false);
  const { setError } = useGlobalNotificationContext();
  const [connectionSettings, setConnectionSettings] =
    useState<ConnectionSettings>(DEFAULT_CONNECTION_SETTINGS);
  const [isConnecting, setIsConnecting] = useState<boolean>(false);
  const [connectionName, setConnectionName] = useState<string>("");
  const [pairingUri, setPairingUri] = useState<string | null>(null);
  const auth = getAuth();
  const currency = auth.getCurrency();

  if (pairingUri) {
    return (
      <PendingConnectionPage
        name={connectionName}
        permissions={connectionSettings.permissionStates.map(
          (permissionState) => permissionState.permission,
        )}
        pairingUri={pairingUri}
      />
    );
  }

  const handleUpdatePermissionStates = (
    permissionStates: PermissionState[],
  ) => {
    setConnectionSettings({
      ...connectionSettings,
      permissionStates,
    });
  };

  const handleHowItWorks = () => {
    setIsHowItWorksVisible(true);
  };

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
    setConnectionSettings({
      ...connectionSettings,
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
    setConnectionSettings({
      ...connectionSettings,
      expirationPeriod,
    });
    setIsEditExpirationVisible(false);
  };

  const handleContinue = () => {
    const today = dayjs();
    const expiration =
      connectionSettings.expirationPeriod === ExpirationPeriod.NONE
        ? undefined
        : today
            .add(
              1,
              connectionSettings.expirationPeriod.toLowerCase() as ManipulateType,
            )
            .toISOString();

    async function submitConnection() {
      setIsConnecting(true);
      const { pairingUri, error } = await initializeManualConnection({
        name: connectionName,
        permissions: connectionSettings.permissionStates
          .filter((permissionState) => permissionState.enabled)
          .map((permissionState) => permissionState.permission.type),
        currencyCode: currency!.code,
        amountInLowestDenom: connectionSettings.amountInLowestDenom,
        limitEnabled: connectionSettings.limitEnabled,
        limitFrequency: connectionSettings.limitFrequency,
        expiration,
      });
      setIsConnecting(false);

      if (error) {
        setError(error);
      }

      setPairingUri(pairingUri);
    }

    submitConnection();
  };

  return (
    <>
      <Intro>
        <Headline size="Large" content="Manual connection" />
        <Description>
          <Body
            size="Large"
            color="grayBlue43"
            content="Manually create a new connection to a NWC-compatible third-party app or service. You'll get a pairing secret to paste or scan in the next step. "
          />
          <Button
            text="How it works"
            kind="ghost"
            onClick={handleHowItWorks}
            typography={{ type: "Body", color: "blue39" }}
            size="Large"
          />
        </Description>
      </Intro>
      <Content>
        <Section>
          <Title content="Connection name" />
          <TextInput
            placeholder="Pick a name for this connection"
            value={connectionName}
            onChange={(value) => setConnectionName(value)}
            activeOutline
          />
        </Section>
        <Section>
          <Title content="Allow this app to" />
          <PermissionsEditableList
            permissionStates={connectionSettings.permissionStates}
            updatePermissionStates={handleUpdatePermissionStates}
          />
        </Section>
        <EditSection onClick={handleEditLimit}>
          <Title
            content={
              connectionSettings.limitEnabled
                ? `${formatConnectionString({ currency, limitFrequency: connectionSettings.limitFrequency, amountInLowestDenom: connectionSettings.amountInLowestDenom })} spending limit`
                : "No spending limit"
            }
          />
          <Icon name="Pencil" width={12} />
        </EditSection>
        <EditSection onClick={handleEditExpiration}>
          <Title
            content={
              connectionSettings.expirationPeriod === ExpirationPeriod.NONE
                ? "Connection never expires"
                : `Connection expires in 1 ${connectionSettings.expirationPeriod.toLowerCase()}`
            }
          />
          <Icon name="Pencil" width={12} />
        </EditSection>
      </Content>

      <ButtonSection>
        <Button
          text="Cancel"
          kind="quaternary"
          externalLink={generatePath(Routes.Root, {})}
        />
        <Button
          text="Continue"
          kind="primary"
          onClick={handleContinue}
          loading={isConnecting}
        />
      </ButtonSection>

      <EditLimit
        title="Edit spending limit"
        visible={isEditLimitVisible}
        amountInLowestDenom={connectionSettings.amountInLowestDenom}
        currency={currency}
        frequency={connectionSettings.limitFrequency}
        enabled={connectionSettings.limitEnabled}
        handleCancel={() => setIsEditLimitVisible(false)}
        handleSubmit={handleSubmitEditLimit}
        isExistingConnection
      />

      <EditExpiration
        title="Expiration date"
        visible={isEditExpirationVisible}
        expirationPeriod={connectionSettings.expirationPeriod}
        handleCancel={() => setIsEditExpirationVisible(false)}
        handleSubmit={handleSubmitEditExpiration}
        isExistingConnection
      />

      <ManualConnectionHowItWorksModal
        visible={isHowItWorksVisible}
        onClose={() => setIsHowItWorksVisible(false)}
      />
    </>
  );
}

const Intro = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.sm};
`;

const Description = styled.div``;

const Content = styled.div`
  display: flex;
  flex-direction: column;

  border-radius: 24px;
  background: ${colors.white};

  & > *:not(:last-child) {
    border-bottom: 1px solid ${colors.gray90};
    padding-bottom: ${Spacing.px["xl"]};
  }
`;

const Section = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.lg};
  width: 100%;
  padding: ${Spacing.px["xl"]};
`;

const EditSection = styled.section`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: ${Spacing.px["xl"]};
  cursor: pointer;
`;

const ButtonSection = styled.section`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
`;
