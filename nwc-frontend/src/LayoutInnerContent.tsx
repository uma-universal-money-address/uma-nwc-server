"use client";

import styled from "@emotion/styled";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import type React from "react";
import GlobalNotificationContext from "src/hooks/useGlobalNotificationContext";
import { NotificationLayout } from "./NotificationLayout";

type Props = {
  children: React.ReactNode;
};

export function LayoutInnerContent({ children }: Props) {
  return (
    <GlobalNotificationContext>
      <NotificationLayout>
        <Container>{children}</Container>
      </NotificationLayout>
    </GlobalNotificationContext>
  );
}

const Container = styled.div`
  display: flex;
  flex-direction: column;
  padding: ${Spacing.px["6xl"]} ${Spacing.px["2xl"]};
  max-width: 800px;
  width: 100%;
  align-self: center;
`;
