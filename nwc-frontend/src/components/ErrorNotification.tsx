import styled from "@emotion/styled";
import {
  CodeBlock,
  Icon,
  Modal,
  UnstyledButton,
} from "@lightsparkdev/ui/components";
import { LabelModerate } from "@lightsparkdev/ui/components/typography/LabelModerate";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { useState } from "react";

export const ErrorNotification = ({
  error,
  clearError,
  clearErrorTimeout,
}: {
  error: Error;
  clearError: () => void;
  clearErrorTimeout: () => void;
}) => {
  const [isErrorModalVisible, setIsErrorModalVisible] = useState(false);

  const handleOpenErrorModal = () => {
    setIsErrorModalVisible(true);
    clearErrorTimeout();
  };

  const handleCloseErrorModal = () => {
    setIsErrorModalVisible(false);
  };

  const handleClose = () => {
    clearError();
  };

  return (
    <Container onClick={handleOpenErrorModal}>
      <Icon name="WarningSign" width={16} />
      <LabelModerate size="Large" content={error.message} />
      <CloseButton onClick={handleClose} type="button">
        <Icon name="Close" width={8} />
      </CloseButton>
      {error && (
        <Modal
          smKind="drawer"
          visible={isErrorModalVisible}
          onClose={handleCloseErrorModal}
          title="Error details"
          description={error.message}
        >
          <CodeBlock withCopyButton language="JSON" title="Error stack trace">
            {error.stack || error.message}
          </CodeBlock>
        </Modal>
      )}
    </Container>
  );
};

const Container = styled.div`
  display: grid;
  grid-auto-flow: column;
  align-items: center;
  grid-template-columns: 24px 1fr auto;
  padding: ${Spacing.md} 20px;
  background-color: ${colors.danger};
  border-radius: 12px;
  box-shadow:
    0px 0px 0px 1px rgba(0, 0, 0, 0.06),
    0px 1px 1px -0.5px rgba(0, 0, 0, 0.06),
    0px 3px 3px -1.5px rgba(0, 0, 0, 0.06),
    0px 6px 6px -3px rgba(0, 0, 0, 0.06),
    0px 12px 12px -6px rgba(0, 0, 0, 0.06),
    0px 24px 24px -12px rgba(0, 0, 0, 0.06);

  color: #fff;
  font-size: 15px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 133.333% */
  letter-spacing: -0.187px;

  margin-top: ${Spacing.md};
  gap: 8px;
  width: 100%;
  max-width: 400px;

  animation: 6s ease-in-out forwards slide-down;

  @keyframes slide-down {
    0% {
      transform: translateY(-20%);
      opacity: 0;
    }
    10% {
      transform: translateY(0%);
      opacity: 1;
    }
    90% {
      transform: translateY(0%);
      opacity: 1;
    }
    100% {
      transform: translateY(-20%);
      opacity: 0;
    }
  }

  cursor: pointer;
`;

const CloseButton = styled(UnstyledButton)`
  width: 24px;
  height: 24px;
  justify-self: flex-end;
`;
