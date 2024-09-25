import styled from "@emotion/styled";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import type React from "react";
import {
  useExchangeRates,
  type ExchangeRates,
} from "src/hooks/useExchangeRates";
import { useTransactions, type Transaction } from "src/hooks/useTransactions";
import { convertCurrency } from "src/utils/convertCurrency";
import { formatTimestamp } from "src/utils/formatTimestamp";
import { Shimmer } from "./Shimmer";

const LoadingTransactionRow = ({ shimmerWidth }: { shimmerWidth: number }) => {
  return (
    <Row>
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

const TransactionRow = ({
  transaction,
  exchangeRates,
}: {
  transaction: Transaction;
  exchangeRates: ExchangeRates;
}) => {
  const isReceiving = transaction.amountInLowestDenom > 0;
  const estimateLocaleString = convertCurrency(
    exchangeRates,
    {
      amount: isReceiving
        ? transaction.amountInLowestDenom
        : -transaction.amountInLowestDenom,
      currencyCode: transaction.currencyCode,
    },
    "USD",
  ).toLocaleString("en", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 8,
  });

  const amount = isReceiving ? (
    <PositiveAmount>{`+${transaction.amountInLowestDenom.toLocaleString("en", {
      maximumFractionDigits: 8,
    })} sats`}</PositiveAmount>
  ) : (
    <Amount>{`${(-transaction.amountInLowestDenom).toLocaleString("en", {
      maximumFractionDigits: 8,
    })} sats`}</Amount>
  );

  return (
    <Row>
      <InfoRowContainer>
        <InfoRow>{amount}</InfoRow>
        <InfoRowDetails>
          <span>{formatTimestamp(transaction.createdAt)}</span>
          <span>{estimateLocaleString}</span>
        </InfoRowDetails>
      </InfoRowContainer>
    </Row>
  );
};

export const TransactionTable = ({
  connectionId,
}: {
  connectionId: string;
}) => {
  const { transactions, isLoading, error } = useTransactions({ connectionId });
  const {
    exchangeRates,
    error: exchangeRatesError,
    isLoading: isLoadingExchangeRates,
  } = useExchangeRates();

  let transactionRows: React.ReactNode;
  if (isLoading || isLoadingExchangeRates) {
    transactionRows = [
      <LoadingTransactionRow key="loader-1" shimmerWidth={30} />,
      <LoadingTransactionRow key="loader-2" shimmerWidth={10} />,
      <LoadingTransactionRow key="loader-3" shimmerWidth={20} />,
    ];
  } else if (error || exchangeRatesError) {
    return <Container>{`Error loading transactions: ${error}`}</Container>;
  } else if (!transactions || !transactions.length) {
    return (
      <EmptyResults>
        <Body content="No transactions yet." />
      </EmptyResults>
    );
  } else {
    transactionRows = transactions.map((transaction) => (
      <TransactionRow
        key={transaction.id}
        transaction={transaction}
        exchangeRates={exchangeRates!}
      />
    ));
  }

  return <Container>{transactionRows}</Container>;
};

const Container = styled.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 24px;
`;

const EmptyResults = styled.div`
  display: flex;
  flex-direction: column;
  place-content: center;
  flex: 1;
`;

const Row = styled.div`
  display: flex;
  flex-direction: row;
  gap: 8px;
  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

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

const Amount = styled.span`
  text-wrap: nowrap;
`;

const PositiveAmount = styled.span`
  color: #19981e;
  text-wrap: nowrap;
`;
