"use client";

import styled from "@emotion/styled";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";

type Props = {
  children: React.ReactNode;
};

export function LayoutInnerContent({ children }: Props) {
  return <Container>{children}</Container>;
}

const Container = styled.div`
  margin-top: ${Spacing["6xl"]};
  max-width: 800px;
  width: 100%;
  align-self: center;
`;
