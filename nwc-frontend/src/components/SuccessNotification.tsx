import styled from "@emotion/styled";

export const SuccessNotification = ({
  successMessage,
}: {
  successMessage: string;
}) => {
  return (
    <Container>
      <img alt="success" src="/icons/success.svg" width={24} height={24} />
      {successMessage}
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: #16171a;
  border-radius: 8px;

  color: #fff;
  font-size: 15px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 133.333% */
  letter-spacing: -0.187px;

  margin-bottom: 12px;
  gap: 8px;
  width: 100%;
  max-width: 400px;
  animation:
    slide-up 0.5s ease-out,
    slide-down 0.5s 4.5s ease-out;

  @keyframes slide-up {
    from {
      transform: translateY(20%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  @keyframes slide-down {
    from {
      transform: translateY(0);
      opacity: 1;
    }
    to {
      transform: translateY(20%);
      opacity: 0;
    }
  }
`;
