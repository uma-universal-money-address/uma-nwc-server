"use client";

import styled from "@emotion/styled";
import { Shimmer } from "./Shimmer";

export const LoadingSkeleton = () => {
  return (
    <Container>
      <Shimmer height={40} />
      <Shimmer height={20} />
      <Shimmer height={20} />
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;
