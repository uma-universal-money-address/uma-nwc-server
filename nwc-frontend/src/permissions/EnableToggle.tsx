import styled from "@emotion/styled";
import { Toggle } from "@lightsparkdev/ui/components";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";

interface Props {
  id: string;
  isEnabled: boolean;
  setIsEnabled: (enabled: boolean) => void;
  title: string;
}

export const EnableToggle = ({ isEnabled, setIsEnabled, title, id }: Props) => {
  return (
    <Container>
      <Text>{title}</Text>
      <Toggle on={isEnabled} onChange={setIsEnabled} id={id} />
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  width: 100%;
  height: 56px;
  padding: ${Spacing.px.sm} ${Spacing.px.md};
  border-radius: 8px;
  background: ${colors.gray95};
`;

const Text = styled.span`
  color: ${({ theme }) => theme.text};
  font-size: 16px;
  line-height: 24px;
  letter-spacing: -0.2px;
`;
