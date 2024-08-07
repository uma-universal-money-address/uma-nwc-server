import { Button } from "@lightsparkdev/ui/components";
import { useNavigate } from "react-router-dom";

export const Nav = () => {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate("/");
  };

  return (
    <Button
      kind="ghost"
      icon="ChevronLeft"
      text="Back to Connections"
      onClick={handleBack}
      typography={{ color: "blue39" }}
    />
  );
};
