import { render } from "@testing-library/react";
import AccountActivation from "./AccountActivation";

describe("account activation page", () => {
  it("should have code, first name, last name, email, password and confirm password fields", () => {
    expect.hasAssertions();
    const { getByLabelText } = render(
      <AccountActivation router={{}} match={{ params: { code: null } }} />
    );
    expect(
      getByLabelText("Code (will be matched against your email)")
    ).toBeInTheDocument();
    expect(getByLabelText("First Name")).toBeInTheDocument();
    expect(getByLabelText("Last Name")).toBeInTheDocument();
    expect(
      getByLabelText("Email (to which address the link was sent)")
    ).toBeInTheDocument();
    expect(getByLabelText("Password")).toBeInTheDocument();
    expect(getByLabelText("Confirm Password")).toBeInTheDocument();
  });
});
