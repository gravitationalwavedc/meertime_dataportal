import { render, waitFor, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PasswordResetRequest from "./PasswordResetRequest";
import { useRouter } from "found";

describe("password reset request page", () => {
  it("should have an email field", () => {
    expect.hasAssertions();
    const { getByLabelText } = render(
      <PasswordResetRequest router={{}} match={{}} />
    );
    expect(getByLabelText("Email")).toBeInTheDocument();
  });

  it("should display errors from the server", async () => {
    expect.hasAssertions();
    const user = userEvent.setup();
    const { router } = useRouter();
    render(
      <PasswordResetRequest
        router={router}
        match={{ params: { next: null } }}
      />
    );

    await user.type(screen.getByLabelText("Email"), "e@mail.com");
    await user.click(screen.getByTestId("password-reset-button"));

    await waitFor(() =>
      expect(
        screen.getByText("Something went wrong, please try later.")
      ).toBeInTheDocument()
    );
  });
});
