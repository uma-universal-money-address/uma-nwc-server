import styled from "@emotion/styled";
import { Icon } from "@lightsparkdev/ui/components";
import { Link } from "react-router-dom";

export const Nav = () => {
  return (
    <Navigation to="/">
      <Icon name="ChevronLeft" width={12} />
      <Text>Back to Connections</Text>
    </Navigation>
  );
};

const Navigation = styled(Link)`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Text = styled.span`
  color: ${({ theme }) => theme.link};
  text-align: center;
  font-size: 17px;
  font-style: normal;
  font-weight: 400;
  line-height: 22px; /* 129.412% */
  letter-spacing: -0.212px;
`;
