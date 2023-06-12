import { render, waitFor, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRouter } from "found";
import Login from "./Login";
import { MockPayloadGenerator } from "relay-test-utils";

describe("login page", () => {
  it("should have a username and password field", () => {
    expect.hasAssertions();
    const { getByLabelText } = render(<Login router={{}} match={{}} />);
    expect(getByLabelText("Email")).toBeInTheDocument();
    expect(getByLabelText("Password")).toBeInTheDocument();
  });

  it("should display errors from the server", async () => {
    expect.hasAssertions();
    const { router } = useRouter();
    const user = userEvent.setup();
    render(<Login router={router} match={{ params: { next: null } }} />);

    const usernameField = screen.getByLabelText("Email");
    const passwordField = screen.getByLabelText("Password");

    await user.type(usernameField, "asher");
    await user.type(passwordField, "password");
    await user.click(screen.getAllByText("Sign in")[1]);

    await waitFor(() => environment.mock.rejectMostRecentOperation());

    await waitFor(() =>
      expect(
        screen.getByText("Please enter valid credentials.")
      ).toBeInTheDocument()
    );
  });
});
