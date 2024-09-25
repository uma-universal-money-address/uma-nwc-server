import styled from "@emotion/styled";
import { colors } from "@lightsparkdev/ui/styles/colors";
import { Shimmer } from "./Shimmer";

interface Props {
  size?: number | undefined;
  uma?: string;
  src?: string;
  isLoading?: boolean;
  shadow?: boolean;
}

export const Avatar = (props: Props) => {
  const avatarSrc = props.src || "/default-app-logo.svg";
  const size = props.size || 48;

  if (props.uma && props.uma.length > 1) {
    return (
      <UmaAvatarContainer width={size} height={size} shadow={!!props.shadow}>
        {props.uma[1].toUpperCase()}
      </UmaAvatarContainer>
    );
  }

  return (
    <AvatarContainer
      shadow={!!props.shadow}
      background={props.src ? "" : colors.gray90}
      padding={props.src ? "0px" : "9px"}
      width={size}
      height={size}
    >
      {props.isLoading ? (
        <Shimmer height={size} width={size} />
      ) : (
        <img
          alt="avatar"
          src={avatarSrc}
          width="100%"
          height="100%"
          style={{
            objectFit: "cover",
          }}
        />
      )}
    </AvatarContainer>
  );
};

const AvatarContainer = styled.div<{
  shadow?: boolean;
  background: string;
  padding: string;
  height: number;
  width: number;
}>`
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  flex-shrink: 0;
  display: flex;
  place-content: center;
  height: fit-content;
  ${(props) => (props.background ? `background: ${props.background};` : "")}
  padding: ${(props) => props.padding};
  width: ${(props) => props.width}px;
  height: ${(props) => props.height}px;
  box-shadow: ${(props) =>
    props.shadow
      ? `0px 0px 0px 1px rgba(0, 0, 0, 0.06),
    0px 1px 1px -0.5px rgba(0, 0, 0, 0.06),
    0px 3px 3px -1.5px rgba(0, 0, 0, 0.06),
    0px 6px 6px -3px rgba(0, 0, 0, 0.06),
    0px 12px 12px -6px rgba(0, 0, 0, 0.06),
    0px 24px 24px -12px rgba(0, 0, 0, 0.06);`
      : "none"};
`;

const UmaAvatarContainer = styled.div<{
  width: number;
  height: number;
  shadow?: boolean;
}>`
  border-radius: 9999px;
  background: #16171a;
  display: flex;
  justify-content: center;
  align-items: center;
  width: ${(props) => props.width}px;
  height: ${(props) => props.height}px;

  color: #fff;
  text-align: center;
  font-size: 16px;
  font-style: normal;
  font-weight: 600;
  line-height: 21px; /* 131.25% */
  letter-spacing: -0.2px;

  box-shadow: ${(props) =>
    props.shadow
      ? `0px 0px 0px 1px rgba(0, 0, 0, 0.06),
    0px 1px 1px -0.5px rgba(0, 0, 0, 0.06),
    0px 3px 3px -1.5px rgba(0, 0, 0, 0.06),
    0px 6px 6px -3px rgba(0, 0, 0, 0.06),
    0px 12px 12px -6px rgba(0, 0, 0, 0.06),
    0px 24px 24px -12px rgba(0, 0, 0, 0.06);`
      : "none"};
`;
