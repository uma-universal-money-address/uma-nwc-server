import styled from "@emotion/styled";
import { Button, Icon } from "@lightsparkdev/ui/components";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import { Label } from "@lightsparkdev/ui/components/typography/Label";
import { Title } from "@lightsparkdev/ui/components/typography/Title";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { Link, useNavigate } from "react-router-dom";
import { generatePath, Routes } from "src/routes/Routes";
import { type Connection, ConnectionStatus } from "src/types/Connection";
import { formatTimestamp } from "src/utils/formatTimestamp";
import { Avatar } from "./Avatar";
import { Shimmer } from "./Shimmer";

export const LoadingConnectionRow = ({
  shimmerWidth,
}: {
  shimmerWidth: number;
}) => {
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
    <LinkRow
      to={generatePath(Routes.ConnectionDetail, {
        connectionId: connection.connectionId,
      })}
    >
      <Avatar size={48} src={connection.avatar ?? ""} />
      <InfoRowContainer>
        <InfoRow>
          <Title content={connection.name} />
        </InfoRow>
        <InfoRowDetails>
          <Label
            size="Large"
            content={
              connection.status === ConnectionStatus.PENDING
                ? "Pending connection"
                : connection.lastUsed
                  ? formatTimestamp(connection.lastUsed, { showTime: true })
                  : ""
            }
          />
        </InfoRowDetails>
      </InfoRowContainer>
      <Icon
        name="CaretRight"
        width={12}
        color="grayBlue43"
        iconProps={{
          strokeWidth: "2",
          strokeLinecap: "round",
          strokeLinejoin: "round",
        }}
      />
    </LinkRow>
  );
};

interface ConnectionTableProps {
  connections: Connection[];
}

export const ConnectionTable = ({ connections }: ConnectionTableProps) => {
  const navigate = useNavigate();

  if (!connections.length) {
    return (
      <EmptyResults>
        <NoTransactionsIcon>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="40"
            height="40"
            viewBox="0 0 40 40"
            fill="none"
          >
            <path
              d="M16.6664 31.6683L16.3805 31.9541C13.777 34.5576 9.55589 34.5576 6.95239 31.9541L6.38048 31.3823C3.77699 28.7788 3.77698 24.5576 6.38048 21.9541L11.9524 16.3823C14.5559 13.7788 18.7769 13.7788 21.3804 16.3823L21.9524 16.9541C23.0418 18.0436 23.6753 19.4161 23.8531 20.835"
              stroke="black"
              strokeWidth="3.33333"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M16.1466 20.8337C16.3243 22.2523 16.958 23.625 18.0473 24.7143L18.6191 25.2862C21.2226 27.8897 25.4438 27.8897 28.0473 25.2862L33.6191 19.7143C36.2226 17.1108 36.2226 12.8897 33.6191 10.2862L33.0473 9.71434C30.4438 7.11084 26.2226 7.11084 23.6191 9.71434L23.3333 10.0003"
              stroke="black"
              strokeWidth="3.33333"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </NoTransactionsIcon>
        <EmptyResultsText>
          <Title size="Medium" content="No connections yet." />
          <Body
            size="Large"
            color="grayBlue43"
            content="Connect your UMA through your favorite apps and services, or manually create a new connection below."
          />
        </EmptyResultsText>
        <Button
          icon={{ name: "Plus" }}
          text="New connection"
          kind="primary"
          onClick={() => navigate(generatePath(Routes.ConnectionNew, {}))}
        />
      </EmptyResults>
    );
  }

  return (
    <Container>
      {connections.map((connection) => (
        <ConnectionRow key={connection.connectionId} connection={connection} />
      ))}
    </Container>
  );
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
  padding: 48px 32px;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  align-self: stretch;
  border-radius: 24px;
  background: #fff;
`;

const LinkRow = styled(Link)`
  display: flex;
  flex-direction: row;
  gap: ${Spacing.px.md};
  cursor: pointer;
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  padding: ${Spacing.px.md} 0;

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

const Row = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${Spacing.px.md};
  cursor: pointer;
  padding: ${Spacing.px.md} 0;
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

const NoTransactionsIcon = styled.div`
  width: 96px;
  height: 96px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f2f3f5;
`;

const EmptyResultsText = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
  text-align: center;
  width: 400px;
`;
