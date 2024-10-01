import styled from "@emotion/styled";
import { Body } from "@lightsparkdev/ui/components/typography/Body";
import type React from "react";
import { useConnection } from "src/hooks/useConnection";
import { useTransactions, type Transaction } from "src/hooks/useTransactions";
import { ConnectionStatus, type Connection } from "src/types/Connection";
import { formatAmountString } from "src/utils/formatConnectionString";
import { formatTimestamp } from "src/utils/formatTimestamp";
import { Shimmer } from "./Shimmer";

const LoadingTransactionRow = ({ shimmerWidth }: { shimmerWidth: number }) => {
  return (
    <Row>
      <TransactionRowContainer>
        <TransactionDetailsRow>
          <Shimmer height={20} width={shimmerWidth + 100} />
          <Shimmer height={20} width={shimmerWidth + 40} />
        </TransactionDetailsRow>
        <TransactionAmountRow>
          <Shimmer height={20} width={shimmerWidth + 30} />
          <Shimmer height={20} width={shimmerWidth + 20} />
        </TransactionAmountRow>
      </TransactionRowContainer>
    </Row>
  );
};

const TransactionRow = ({
  connection,
  transaction,
}: {
  connection: Connection;
  transaction: Transaction;
}) => {
  const amount = (
    <Amount>
      {formatAmountString({
        currency: connection.budgetCurrency,
        amountInLowestDenom: transaction.budgetAmountInLowestDenom,
      })}
    </Amount>
  );

  return (
    <Row>
      <TransactionRowContainer>
        <TransactionDetailsRow>
          <span>{formatTimestamp(transaction.createdAt)}</span>
          {amount}
        </TransactionDetailsRow>
      </TransactionRowContainer>
    </Row>
  );
};

export const TransactionTable = ({
  connectionId,
}: {
  connectionId: string;
}) => {
  const {
    connection,
    isLoading: isLoadingConnection,
    error: connectionError,
  } = useConnection({ connectionId });
  const {
    transactions,
    isLoading: isLoadingTransactions,
    error: transactionsError,
  } = useTransactions({ connectionId });

  let transactionRows: React.ReactNode;
  if (isLoadingTransactions || isLoadingConnection) {
    transactionRows = [
      <LoadingTransactionRow key="loader-1" shimmerWidth={30} />,
      <LoadingTransactionRow key="loader-2" shimmerWidth={10} />,
      <LoadingTransactionRow key="loader-3" shimmerWidth={20} />,
    ];
  } else if (connectionError || !connection) {
    return (
      <Container>{`Error loading connection: ${connectionError}`}</Container>
    );
  } else if (transactionsError) {
    return (
      <Container>{`Error loading transactions: ${transactionsError}`}</Container>
    );
  } else if (!transactions || !transactions.length) {
    return (
      <EmptyResults>
        <Body
          content={
            connection.status === ConnectionStatus.INACTIVE
              ? "No transactions."
              : "No transactions yet."
          }
        />
      </EmptyResults>
    );
  } else {
    transactionRows = transactions.map((transaction) => (
      <TransactionRow
        key={transaction.id}
        transaction={transaction}
        connection={connection}
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

const TransactionRowContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
  justify-content: center;
  flex-grow: 1;
`;

const TransactionDetailsRow = styled.div`
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

const TransactionAmountRow = styled.div`
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
