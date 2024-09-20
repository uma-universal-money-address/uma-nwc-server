import styled from "@emotion/styled";
import { Button, Icon } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { QRCodeSVG } from "qrcode.react";
import { Avatar } from "src/components/Avatar";
import { useGlobalNotificationContext } from "src/hooks/useGlobalNotificationContext";
import { PermissionsList } from "src/permissions/PermissionsList";
import { type Permission } from "src/types/Connection";

interface Props {
  name: string;
  permissions: Permission[];
  /** Pairing URI only provided upon first creating a manual connection. */
  pairingUri?: string;
}

export const PendingConnectionPage = ({
  name,
  permissions,
  pairingUri,
}: Props) => {
  const { setSuccessMessage } = useGlobalNotificationContext();

  const handleCopyConnectionString = () => {
    (async () => {
      await navigator.clipboard.writeText(pairingUri);
      setSuccessMessage("Connection string copied to clipboard");
    })();
  };

  return (
    <>
      {pairingUri && (
        <Intro>
          <Title size="Large" content="Connect your UMA" />
          <Description>
            <Body content="Scan the QR code below with the app you want to connect. Or, manually copy and paste the connection string inside the app. " />
          </Description>
        </Intro>
      )}
      <Content>
        <Section>
          <PermissionsAndQRCode>
            <Info>
              <AppSection>
                <Avatar size={48} />
                <AppName>{name}</AppName>
              </AppSection>
              <Permissions>
                <Title size="Medium" content="This app will be able to" />
                <PermissionsList permissions={permissions} />
              </Permissions>
            </Info>
            {pairingUri && (
              <QRCodeSection>
                <QRCodeContainer>
                  <QRCodeSVG value={pairingUri} width="100%" height="100%" />
                </QRCodeContainer>
                <Button
                  icon="Copy"
                  text="Copy connection string"
                  kind="primary"
                  onClick={handleCopyConnectionString}
                  fullWidth
                />
              </QRCodeSection>
            )}
          </PermissionsAndQRCode>
        </Section>
        {pairingUri && (
          <Section>
            <Warning>
              <Icon name="WarningSign" width={12} />
              <Body content="For security, this QR code and connection string are only available once. If you navigate away from this screen, you won't be able to retrieve them." />
            </Warning>
          </Section>
        )}
      </Content>
    </>
  );
};

const Intro = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.sm};
`;

const Description = styled.div``;

const Content = styled.div`
  display: flex;
  flex-direction: column;

  border-radius: 24px;
  background: ${colors.white};

  & > *:not(:last-child) {
    border-bottom: 1px solid ${colors.gray90};
    padding-bottom: ${Spacing["xl"]};
  }
`;

const Section = styled.section`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.lg};
  width: 100%;
  padding: ${Spacing["xl"]};
`;

const AppSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${Spacing.sm};
`;

const AppName = styled.span`
  font-size: 16px;
  font-style: normal;
  font-weight: 600;
  line-height: 24px;
  letter-spacing: -0.2px;
`;

const PermissionsAndQRCode = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${Spacing["5xl"]};
  justify-content: space-between;
`;

const Info = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.lg};
`;

const Permissions = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.sm};
`;

const QRCodeSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.md};
`;

const QRCodeContainer = styled.div`
  width: 336px;
  height: 336px;
  padding: ${Spacing.xl};
  border-radius: 16px;
  border: 1px solid ${colors.gray90};
`;

const Warning = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${Spacing.sm};
  align-items: center;
`;
