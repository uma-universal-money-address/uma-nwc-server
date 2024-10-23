import styled from "@emotion/styled";
import { UnstyledButton } from "@lightsparkdev/ui/components";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { LimitFrequency } from "src/types/Connection";

interface Props {
  frequency: LimitFrequency;
  setFrequency: (frequency: LimitFrequency) => void;
}

export const LimitFrequencyPicker = ({ frequency, setFrequency }: Props) => {
  const handleChooseFrequency =
    (frequency: LimitFrequency) => (e: React.MouseEvent<HTMLButtonElement>) => {
      setFrequency(frequency);
      e.preventDefault();
    };

  return (
    <Container>
      {Object.values(LimitFrequency)
        .filter(
          (limitFrequencyOption) =>
            limitFrequencyOption !== LimitFrequency.NONE,
        )
        .map((frequencyOption) => (
          <FrequencyButton
            key={frequencyOption}
            selected={frequencyOption === frequency}
            onClick={handleChooseFrequency(frequencyOption)}
          >
            {frequencyOption}
          </FrequencyButton>
        ))}
    </Container>
  );
};

const Container = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
`;

const FrequencyButton = styled(UnstyledButton)<{ selected: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${Spacing.px.sm} ${Spacing.px.md};
  border-radius: 8px;
  border: ${({ selected }) =>
    selected ? "2px solid #16171A" : ".5px solid #C0C9D6"};

  color: ${({ selected }) => (selected ? "#16171A" : "#686A72")};
  font-size: 14px;
  line-height: 20px;
  letter-spacing: -0.175px;
`;
