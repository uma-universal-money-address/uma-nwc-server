import styled from "@emotion/styled";
import { Icon } from "@lightsparkdev/ui/components";
import { LabelModerate } from "@lightsparkdev/ui/components/typography/LabelModerate";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";

export const SuccessNotification = ({
  successMessage,
}: {
  successMessage: string;
}) => {
  return (
    <Container>
      <LabelModerate size="Large" content={successMessage} />
      <Icon name="Close" width={8} />
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${Spacing.px.md} 20px;
  background-color: #16171a;
  border-radius: 12px;
  box-shadow:
    0px 0px 0px 1px rgba(0, 0, 0, 0.06),
    0px 1px 1px -0.5px rgba(0, 0, 0, 0.06),
    0px 3px 3px -1.5px rgba(0, 0, 0, 0.06),
    0px 6px 6px -3px rgba(0, 0, 0, 0.06),
    0px 12px 12px -6px rgba(0, 0, 0, 0.06),
    0px 24px 24px -12px rgba(0, 0, 0, 0.06);

  color: #fff;
  font-size: 15px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 133.333% */
  letter-spacing: -0.187px;

  margin-top: ${Spacing.px.md};
  gap: 8px;
  width: 100%;
  max-width: 400px;
  animation: 6s ease-in-out forwards slide-down;

  @keyframes slide-down {
    0% {
      transform: translateY(-20%);
      opacity: 0;
    }
    10% {
      transform: translateY(0%);
      opacity: 1;
    }
    90% {
      transform: translateY(0%);
      opacity: 1;
    }
    100% {
      transform: translateY(-20%);
      opacity: 0;
    }
  }

  cursor: pointer;
`;
