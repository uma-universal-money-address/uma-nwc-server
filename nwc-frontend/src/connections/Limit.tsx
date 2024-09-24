import styled from "@emotion/styled";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import dayjs from "dayjs";
import { type Connection, LimitFrequency } from "src/types/Connection";
import {
  formatAmountString,
  FREQUENCY_TO_SINGULAR_FORM,
} from "src/utils/formatConnectionString";

const RENEWAL_DATE_FUNCTIONS = {
  [LimitFrequency.DAILY]: (createdAt: dayjs.Dayjs) => createdAt.add(1, "day"),
  [LimitFrequency.WEEKLY]: (createdAt: dayjs.Dayjs) => createdAt.add(1, "week"),
  [LimitFrequency.MONTHLY]: (createdAt: dayjs.Dayjs) =>
    createdAt.add(1, "month"),
};

export const Limit = ({ connection }: { connection: Connection }) => {
  let renewsIn = "";

  if (!connection.limitEnabled) {
    return (
      <Container>
        <Row>
          <LimitValue>No spending limit</LimitValue>
        </Row>
      </Container>
    );
  }

  if (
    connection.limitFrequency === LimitFrequency.NONE ||
    !connection.limitFrequency
  ) {
    if (connection.expiresAt) {
      const expirationDate = dayjs(connection.expiresAt);
      const daysUntilExpiration = expirationDate.diff(dayjs(), "days");
      if (daysUntilExpiration < 0) {
        // Shouldn't happen
        renewsIn = "Error";
      } else if (daysUntilExpiration === 0) {
        renewsIn = `Expires today at ${expirationDate.format("HH:mm")}`;
      } else if (daysUntilExpiration === 1) {
        renewsIn = `Expires tomorrow at ${expirationDate.format("HH:mm")}`;
      } else {
        renewsIn = `Expires in ${daysUntilExpiration} days`;
      }
    } else {
      renewsIn = "Does not expire";
    }
  } else {
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
  }

  const amountUsed = connection.amountInLowestDenomUsed || 0;
  const amount = connection.amountInLowestDenom || 0;
  const amountUsedString = `${formatAmountString({ currency: connection.budgetCurrency, amountInLowestDenom: amountUsed })} used`;
  const amountRemainingString = `${formatAmountString({ currency: connection.budgetCurrency, amountInLowestDenom: amount - amountUsed })} remaining`;
  const limitFrequencyString =
    connection.limitFrequency &&
    connection.limitFrequency !== LimitFrequency.NONE
      ? ` per ${FREQUENCY_TO_SINGULAR_FORM[connection.limitFrequency]}`
      : "";

  return (
    <Container>
      <Row>
        <LimitValue>{`${formatAmountString({ currency: connection.budgetCurrency, amountInLowestDenom: amount })}${limitFrequencyString}`}</LimitValue>
        <LimitBar>
          <LimitBarFill
            style={{
              width: `${(amountUsed / amount) * 100}%`,
            }}
          />
        </LimitBar>
      </Row>
      <Row>
        <RenewsIn>{renewsIn}</RenewsIn>
        <Amounts>
          <div>{amountUsedString}</div>
          <div>{amountRemainingString}</div>
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
