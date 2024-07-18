"use client";

import styled from "@emotion/styled";
import { Icon } from "@lightsparkdev/ui/components";
import { Link } from "react-router-dom";

export const Header = () => {
  return (
    <Container to="/">
      <Icon name="ChevronLeft" width={12} />
      <HeaderText>Back to Connections</HeaderText>
    </Container>
  );
};

const Container = styled(Link)`
  padding: 16px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
`;

const HeaderText = styled.span`
  color: ${({ theme }) => theme.link};
  text-align: center;
  font-size: 17px;
  font-style: normal;
  font-weight: 400;
  line-height: 22px; /* 129.412% */
  letter-spacing: -0.212px;
`;
