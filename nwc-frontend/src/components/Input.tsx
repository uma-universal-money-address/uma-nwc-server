import styled from "@emotion/styled";
import { Label } from "@lightsparkdev/ui/components/typography/Label";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import React, {
  useEffect,
  useState,
  type DetailedHTMLProps,
  type InputHTMLAttributes,
  type KeyboardEvent,
} from "react";

interface Props {
  inputProps: DetailedHTMLProps<
    InputHTMLAttributes<HTMLInputElement>,
    HTMLInputElement
  >;
  before?: string;
  after?: string;
  error?: string | null;
  onEnter?: () => void;
  innerRef?: React.Ref<HTMLInputElement>;
}

export const Input = ({
  before,
  after,
  inputProps,
  error,
  onEnter,
  innerRef,
}: Props) => {
  const [hasError, setHasError] = useState(false);

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && onEnter) {
      onEnter();
    }
  };

  useEffect(() => {
    setHasError(Boolean(error && error.length));
  }, [error]);

  return (
    <Container>
      <InputContainer hasError={hasError}>
        {before ? <SubHeadline>{before}</SubHeadline> : null}
        <InputElement
          {...inputProps}
          onKeyDown={(e) => {
            if (inputProps.onKeyDown) {
              inputProps.onKeyDown(e);
            }
            handleKeyDown(e);
          }}
          ref={innerRef}
        />
        {after ? <SubHeadline>{after}</SubHeadline> : null}
      </InputContainer>
      {error ? (
        <Label size="Small" color="danger">
          {error}
        </Label>
      ) : null}
    </Container>
  );
};

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing["3xs"]};
  width: 100%;
`;

const InputContainer = styled.div<{ hasError: boolean }>`
  border: 1px solid #e0e0e0;
  border-color: ${({ hasError }) => (hasError ? "#D80027" : "#e0e0e0")};
  border-radius: 8px;
  display: flex;
  align-items: center;
  height: 48px;
  padding: 16px 12px 16px 16px;
  gap: 10px;

  *:focus-visible {
    outline: none;
  }
`;

const SubHeadline = styled.span`
  color: #16171a;
  font-size: 15px;
  font-style: normal;
  font-weight: 400;
  line-height: 20px; /* 133.333% */
  letter-spacing: -0.187px;
  text-wrap: nowrap;
`;

const InputElement = styled.input`
  width: 100%;
  border: none;
  background: none;

  ${SubHeadline}
`;
