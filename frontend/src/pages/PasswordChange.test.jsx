import { fireEvent, render } from "@testing-library/react";
import PasswordChange from "./PasswordChange";

describe("password change page", () => {
  it("should have current, new and confirm new password fields", () => {
    expect.hasAssertions();
    const { getByLabelText } = render(
      <PasswordChange router={{}} match={{}} />
    );
    expect(getByLabelText("Current Password")).toBeInTheDocument();
    expect(getByLabelText("New Password")).toBeInTheDocument();
    expect(getByLabelText("Confirm New Password")).toBeInTheDocument();
  });
});
