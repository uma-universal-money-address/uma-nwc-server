import styled from "@emotion/styled";
import { Icon } from "@lightsparkdev/ui/components";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { type Permission } from "src/types/Connection";

export const PermissionsList = ({
  permissions,
}: {
  permissions: (Permission | string)[];
}) => {
  return (
    <List>
      {permissions.map((permission) => {
        if (typeof permission === "string") {
          return (
            <PermissionRow key={permission}>
              <Icon name="CheckmarkCircleTier1" width={20} />
              {permission}
            </PermissionRow>
          );
        }

        return (
          <PermissionRow key={permission.type}>
            <Icon name="CheckmarkCircleTier1" width={20} />
            {permission.description}
          </PermissionRow>
        );
      })}
    </List>
  );
};

const List = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px["3xs"]};
  width: 100%;
`;

const PermissionRow = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: ${Spacing.px["3xs"]};

  font-size: 16px;
  font-style: normal;
  font-weight: 500;
  line-height: 24px; /* 150% */
`;
