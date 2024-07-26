import styled from "@emotion/styled";
import { Icon } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import React from "react";
import { Link } from "react-router-dom";
import { useConnections, type Connection } from "src/hooks/useConnections";
import { formatTimestamp } from "src/utils/formatTimestamp";
import { Avatar } from "./Avatar";
import { Shimmer } from "./Shimmer";

const LoadingConnectionRow = ({ shimmerWidth }: { shimmerWidth: number }) => {
  return (
    <Row>
      <Avatar size={48} />
      <InfoRowContainer>
        <InfoRow>
          <Shimmer height={20} width={shimmerWidth + 100} />
          <Shimmer height={20} width={shimmerWidth + 40} />
        </InfoRow>
        <InfoRowDetails>
          <Shimmer height={20} width={shimmerWidth + 30} />
          <Shimmer height={20} width={shimmerWidth + 20} />
        </InfoRowDetails>
      </InfoRowContainer>
    </Row>
  );
};

const ConnectionRow = ({ connection }: { connection: Connection }) => {
  return (
    <Row to={`/connection/${connection.appId}`}>
      <Avatar size={48} src={connection.avatar} />
      <InfoRowContainer>
        <InfoRow>
          <span>{connection.name}</span>
        </InfoRow>
        <InfoRowDetails>
          <span>{formatTimestamp(connection.lastUsed)}</span>
        </InfoRowDetails>
      </InfoRowContainer>
      <Icon name="CaretRight" width={12} color="#686a72" />
    </Row>
  );
};

export const ConnectionTable = () => {
  const { connections, isLoading, error } = useConnections();

  let connectionRows: React.ReactNode;
  if (isLoading) {
    connectionRows = [
      <LoadingConnectionRow key="loader-1" shimmerWidth={30} />,
      <LoadingConnectionRow key="loader-2" shimmerWidth={10} />,
      <LoadingConnectionRow key="loader-3" shimmerWidth={20} />,
    ];
  } else if (error) {
    return <Container>{`Error loading connections: ${error}`}</Container>;
  } else if (!connections || !connections.length) {
    return (
      <EmptyResults>
        <Body content="No connections yet." />
      </EmptyResults>
    );
  } else {
    connectionRows = connections.map((connection) => (
      <ConnectionRow key={connection.appId} connection={connection} />
    ));
  }

  return <Container>{connectionRows}</Container>;
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 24px;
  background: #fff;
`;

const EmptyResults = styled.div`
  display: flex;
  flex-direction: column;
  place-content: center;
  flex: 1;
`;

const Row = styled(Link)`
  display: flex;
  flex-direction: row;
  gap: ${Spacing.md};
  cursor: pointer;
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  padding: ${Spacing.md} 0;

  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;

  div,
  span {
    -webkit-user-select: none; /* Safari */
    -ms-user-select: none; /* IE 10 and IE 11 */
    user-select: none; /* Standard syntax */
  }
`;

const InfoRowContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
  justify-content: center;
  flex-grow: 1;
`;

const InfoRow = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 8px;

  color: #16171a;
  font-size: 15px;
  font-style: normal;
  font-weight: 500;
  line-height: 20px; /* 133.333% */
  letter-spacing: -0.187px;
`;

const InfoRowDetails = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 8px;

  color: #686a72;
  font-size: 15px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 133.333% */
  letter-spacing: -0.187px;
`;
