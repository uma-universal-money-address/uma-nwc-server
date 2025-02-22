import styled from "@emotion/styled";
import { Checkbox } from "@lightsparkdev/ui/components";
import { Spacing } from "@lightsparkdev/ui/styles/tokens/spacing";
import { type PermissionState } from "src/types/Connection";

interface Props {
  permissionStates: PermissionState[];
  updatePermissionStates: (permissionStates: PermissionState[]) => void;
}

export const PermissionsEditableList = ({
  permissionStates,
  updatePermissionStates,
}: Props) => {
  const handleCheckboxChange = (permissionState: PermissionState) => () => {
    const isEnabled = !permissionState.enabled;
    updatePermissionStates(
      permissionStates.map((ps) => {
        if (ps.permission.type === permissionState.permission.type) {
          return {
            ...ps,
            enabled: isEnabled,
          };
        }
        return ps;
      }),
    );
  };

  return (
    <List>
      {permissionStates.map((permissionState) => (
        <PermissionRow key={permissionState.permission.type}>
          <Checkbox
            checked={permissionState.enabled}
            onChange={handleCheckboxChange(permissionState)}
            disabled={!permissionState.permission.optional}
          />
          {permissionState.permission.description}
        </PermissionRow>
      ))}
    </List>
  );
};

const List = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${Spacing.px.sm};
  width: 100%;
`;

const PermissionRow = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: ${Spacing.px.xs};

  font-size: 16px;
  font-style: normal;
  font-weight: 500;
  line-height: 24px; /* 150% */
`;
