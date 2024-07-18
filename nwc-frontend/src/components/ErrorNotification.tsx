import styled from "@emotion/styled";
import {
  CodeBlock,
  Icon,
  Modal,
  UnstyledButton,
} from "@lightsparkdev/ui/components";
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
      <WarningIcon>
        <img alt="error" src="/error.svg" width={24} height={24} />
      </WarningIcon>
      {error.message}
      <CloseButton onClick={handleClose} type="button">
        <Icon name="Close" width={12} />
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
  padding: 16px;
  background-color: #e31a1a;
  border-radius: 8px;

  color: #fff;
  font-size: 15px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 133.333% */
  letter-spacing: -0.187px;

  margin-bottom: 12px;
  gap: 8px;
  width: 100%;
  max-width: 400px;
  animation: slide-up 0.5s ease-out;

  @keyframes slide-up {
    from {
      transform: translateY(20%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  cursor: pointer;
`;

const WarningIcon = styled.div`
  width: fit-content;
`;

const CloseButton = styled(UnstyledButton)`
  width: 24px;
  height: 24px;
  justify-self: flex-end;
`;
