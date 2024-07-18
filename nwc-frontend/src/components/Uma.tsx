import styled from "@emotion/styled";
import { Shimmer } from "./Shimmer";

export const Uma = ({
  uma,
  isLoading,
}: {
  uma?: string;
  isLoading?: boolean;
}) => {
  return (
    <Container>
      <Text>
        {uma && !isLoading ? uma : <Shimmer height={20} width={120} />}
      </Text>
      <img alt="uma" src="/uma.svg" width={28} height={12} />
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: row;
  gap: 6px;
  align-items: center;
  justify-content: center;
  width: 100%;
`;

const Text = styled.span`
  color: #686a72;
  font-size: 15px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 133.333% */
  letter-spacing: -0.187px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`;
