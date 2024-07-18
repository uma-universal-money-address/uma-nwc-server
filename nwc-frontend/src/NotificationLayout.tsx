import styled from "@emotion/styled";
import React from "react";
import { ErrorNotification } from "src/components/ErrorNotification";
import { SuccessNotification } from "src/components/SuccessNotification";
import { useGlobalNotificationContext } from "src/hooks/useGlobalNotificationContext";

export const NotificationLayout = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const {
    error,
    successMessage,
    clearNotifications,
    clearErrorTimeout,
    setError,
  } = useGlobalNotificationContext();

  return (
    <>
      {children}
      <NotificationContainer onClick={clearNotifications}>
        {error && (
          <ErrorNotification
            error={error}
            clearError={() => setError(null)}
            clearErrorTimeout={clearErrorTimeout}
          />
        )}
        {successMessage && (
          <SuccessNotification successMessage={successMessage} />
        )}
      </NotificationContainer>
    </>
  );
};

const NotificationContainer = styled.div`
  position: absolute;
  bottom: 0;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
`;
