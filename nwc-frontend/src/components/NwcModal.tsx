import styled from "@emotion/styled";
import { Icon, Modal, UnstyledButton } from "@lightsparkdev/ui/components";

interface Props {
  visible: boolean;
  onClose: () => void;
  children: React.ReactNode;
  buttons: React.ReactNode;
  width?: number;
  onSubmit?: () => void;
}

export const NwcModal = ({
  visible,
  onSubmit,
  onClose,
  width,
  children,
  buttons,
}: Props) => {
  return (
    <Modal
      ghost
      width={width || 480}
      smKind="drawer"
      visible={visible}
      cancelHidden
      onClose={onClose}
      onCancel={onClose}
      onSubmit={onSubmit}
    >
      <ModalContents>
        <Header>
          <CloseButton onClick={onClose} type="button">
            <Icon
              name="Close"
              width={10}
              color="grayBlue43"
              iconProps={{
                strokeWidth: "1.2",
                strokeLinecap: "round",
                strokeLinejoin: "round",
              }}
            />
          </CloseButton>
        </Header>
        <Children>{children}</Children>
        <ButtonSection>{buttons}</ButtonSection>
      </ModalContents>
    </Modal>
  );
};

const ModalContents = styled.div`
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 24px;
  box-shadow:
    0px 0px 0px 1px rgba(0, 0, 0, 0.06),
    0px 1px 1px -0.5px rgba(0, 0, 0, 0.06),
    0px 3px 3px -1.5px rgba(0, 0, 0, 0.06),
    0px 6px 6px -3px rgba(0, 0, 0, 0.06),
    0px 12px 12px -6px rgba(0, 0, 0, 0.06),
    0px 24px 24px -12px rgba(0, 0, 0, 0.06);
`;

const Children = styled.div`
  display: flex;
  flex-direction: column;
  padding: 0 32px 32px 32px;
`;

const Header = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16px;
  padding: 24px 24px 0px 24px;
`;

const CloseButton = styled(UnstyledButton)`
  display: flex;
  justify-content: center;
  align-items: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;

  &:hover {
    background: #00000005;
  }

  &:active {
    background: #00000014;
  }
`;

const ButtonSection = styled.div`
  display: flex;
  padding: 20px 24px;
  justify-content: flex-end;
  align-items: center;
  border-top: 0.5px solid #c0c9d6;
`;
