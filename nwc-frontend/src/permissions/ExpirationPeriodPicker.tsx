import styled from "@emotion/styled";
import { UnstyledButton } from "@lightsparkdev/ui/components";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { ExpirationPeriod } from "src/types/Connection";

interface Props {
  expirationPeriod: ExpirationPeriod;
  setExpirationPeriod: (expirationPeriod: ExpirationPeriod) => void;
}

export const ExpirationPeriodPicker = ({
  expirationPeriod,
  setExpirationPeriod,
}: Props) => {
  const handleChooseExpiration =
    (expirationPeriod: ExpirationPeriod) =>
    (e: React.MouseEvent<HTMLButtonElement>) => {
      setExpirationPeriod(expirationPeriod);
      e.preventDefault();
    };

  return (
    <Container>
      {Object.values(ExpirationPeriod)
        .filter(
          (expirationPeriodOption) =>
            expirationPeriodOption !== ExpirationPeriod.NONE,
        )
        .map((expirationPeriodOption) => (
          <ExpirationPeriodButton
            key={expirationPeriodOption}
            selected={expirationPeriodOption === expirationPeriod}
            onClick={handleChooseExpiration(expirationPeriodOption)}
          >
            1 {expirationPeriodOption.toLowerCase()}
          </ExpirationPeriodButton>
        ))}
    </Container>
  );
};

const Container = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
`;

const ExpirationPeriodButton = styled(UnstyledButton)<{ selected: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${Spacing.sm} ${Spacing.md};
  border-radius: 8px;
  border: 1px solid ${({ theme }) => theme.lcNeutral};
  opacity: ${({ selected }) => (selected ? 1 : 0.4)};
  transition: opacity 0.2s;

  color: ${({ theme }) => theme.text};
  font-size: 14px;
  line-height: 20px;
  letter-spacing: -0.175px;

  &:hover {
    opacity: 1;
  }
`;
