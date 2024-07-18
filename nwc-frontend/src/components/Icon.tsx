import styled from "@emotion/styled";

interface Props {
  icon?: string;
  emoji?: string;
  alt?: string;
}

export const Icon = ({ icon, emoji, alt }: Props) => {
  if (icon) {
    return <img src={icon} alt={alt || ""} width={24} height={24} />;
  } else if (emoji) {
    return <EmojiIcon>{emoji}</EmojiIcon>;
  } else {
    return <EmojiIcon>{"∅"}</EmojiIcon>;
  }
};

const EmojiIcon = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
`;
