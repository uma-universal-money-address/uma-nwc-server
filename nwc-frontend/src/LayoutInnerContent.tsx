"use client";

import styled from "@emotion/styled";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import type React from "react";

type Props = {
  children: React.ReactNode;
};

export function LayoutInnerContent({ children }: Props) {
  return <Container>{children}</Container>;
}

const Container = styled.div`
  display: flex;
  flex-direction: column;
  padding: ${Spacing["6xl"]} ${Spacing["2xl"]};
  max-width: 800px;
  width: 100%;
  align-self: center;
`;
