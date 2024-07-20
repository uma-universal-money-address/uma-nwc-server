import styled from "@emotion/styled";
import { UnstyledButton } from "@lightsparkdev/ui/components";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { LimitFrequency } from "src/types/Connection";

interface Props {
  frequency: LimitFrequency;
  setFrequency: (frequency: LimitFrequency) => void;
}

export const LimitFrequencyPicker = ({ frequency, setFrequency }: Props) => {
  const handleChooseFrequency = (frequency) => (e) => {
    setFrequency(frequency);
    e.preventDefault();
  }

  return (
    <Container>
      {Object.values(LimitFrequency).map((frequencyOption) => (
        <FrequencyButton
          key={frequencyOption}
          selected={frequencyOption === frequency}
          onClick={handleChooseFrequency(frequencyOption)}
        >
          {frequencyOption}
        </FrequencyButton>
      ))}
    </Container>
  )
}

const Container = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
`;

const FrequencyButton = styled(UnstyledButton)<{ selected: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${Spacing.sm} ${Spacing.md};
  border-radius: 8px;
  border: 1px solid ${({ theme }) => theme.border};
  opacity: ${({ selected }) => selected ? 1 : 0.4};
  transition: opacity 0.2s;

  color: ${({ theme }) => theme.text};
  font-size: 14px;
  line-height: 20px;
  letter-spacing: -0.175px;

  &:hover {
    opacity: 1;
  }
`;
