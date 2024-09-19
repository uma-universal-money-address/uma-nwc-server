import styled from "@emotion/styled";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import dayjs from "dayjs";
import { Connection, LimitFrequency } from "src/types/Connection";
import { convertToNormalDenomination } from "src/utils/convertToNormalDenomination";
import { FREQUENCY_TO_SINGULAR_FORM } from "src/utils/formatConnectionString";

const RENEWAL_DATE_FUNCTIONS = {
  [LimitFrequency.DAILY]: (createdAt: dayjs.Dayjs) => createdAt.add(1, "day"),
  [LimitFrequency.WEEKLY]: (createdAt: dayjs.Dayjs) => createdAt.add(1, "week"),
  [LimitFrequency.MONTHLY]: (createdAt: dayjs.Dayjs) =>
    createdAt.add(1, "month"),
};

export const Limit = ({ connection }: { connection: Connection }) => {
  let renewsIn = "";
  if (connection.limitEnabled) {
    if (connection.limitFrequency === LimitFrequency.NONE) {
      return (
        <Container>
          <Row>
            <LimitValue>No renewal</LimitValue>
          </Row>
        </Container>
      );
    }

    const createdAt = dayjs(connection.createdAt);
    const renewalDate =
      RENEWAL_DATE_FUNCTIONS[connection.limitFrequency](createdAt);
    const daysUntilRenewal = renewalDate.diff(dayjs(), "days");
    if (daysUntilRenewal < 0) {
      // Shouldn't happen
      renewsIn = "Error";
    } else if (daysUntilRenewal === 0) {
      renewsIn = `Renews today at ${renewalDate.format("HH:mm")}`;
    } else if (daysUntilRenewal === 1) {
      renewsIn = `Renews tomorrow at ${renewalDate.format("HH:mm")}`;
    } else {
      renewsIn = `Renews in ${daysUntilRenewal} days`;
    }
  } else {
    return (
      <Container>
        <Row>
          <LimitValue>No spending limit</LimitValue>
        </Row>
      </Container>
    );
  }

  const amountUsed = `${connection.currency.symbol}${convertToNormalDenomination(connection.amountInLowestDenomUsed, connection.currency)} used`;
  const amountRemaining = `${connection.currency.symbol}${convertToNormalDenomination(connection.amountInLowestDenom - connection.amountInLowestDenomUsed, connection.currency)} remaining`;

  return (
    <Container>
      <Row>
        <LimitValue>{`${connection.currency.symbol}${convertToNormalDenomination(connection.amountInLowestDenom, connection.currency)} per ${FREQUENCY_TO_SINGULAR_FORM[connection.limitFrequency]}`}</LimitValue>
        <LimitBar>
          <LimitBarFill
            style={{
              width: `${(connection.amountInLowestDenomUsed / connection.amountInLowestDenom) * 100}%`,
            }}
          />
        </LimitBar>
      </Row>
      <Row>
        <RenewsIn>{renewsIn}</RenewsIn>
        <Amounts>
          <div>{amountUsed}</div>
          <div>{amountRemaining}</div>
        </Amounts>
      </Row>
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: ${Spacing.md};
`;

const Row = styled.div`
  display: flex;
  flex-direction: row;
  gap: ${Spacing["3xs"]};
  width: 100%;
  align-items: center;
  justify-content: space-between;
`;

const RenewsIn = styled.span`
  font-size: 16px;
  font-weight: 400;
`;

const RightSide = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing["3xs"]};
`;

const LimitValue = styled.span`
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
`;

const LimitBar = styled.div`
  width: 50%;
  height: 6px;
  border-radius: 999px;
  background: #ebeef2;
`;

const LimitBarFill = styled.div`
  height: 100%;
  border-radius: 999px;
  background: #0068c9;
`;

const Amounts = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  width: 50%;
  gap: ${Spacing["3xs"]};
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
`;
