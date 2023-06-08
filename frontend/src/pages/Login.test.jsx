import { fireEvent, render, waitFor, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRouter } from "found";
import Login from "./Login";
import { MockPayloadGenerator } from "relay-test-utils";
import environment from "../relayEnvironment";

describe("login page", () => {
  it("should have a username and password field", () => {
    expect.hasAssertions();
    const { getByLabelText } = render(<Login router={{}} match={{}} />);
    expect(getByLabelText("Email")).toBeInTheDocument();
    expect(getByLabelText("Password")).toBeInTheDocument();
  });

  it("should submit when there is a username and password", async () => {
    expect.hasAssertions();
    const { router } = useRouter();
    const { getAllByText, getByLabelText } = render(
      <Login router={router} match={{ params: { next: null } }} />
    );
    const usernameField = getByLabelText("Email");
    const passwordField = getByLabelText("Password");
    fireEvent.change(usernameField, { target: { value: "asher" } });
    fireEvent.change(passwordField, { target: { value: "password" } });
    fireEvent.click(getAllByText("Sign in")[1]);
    const operation = await waitFor(() =>
      environment.mock.getMostRecentOperation()
    );
    environment.mock.resolve(
      operation,
      MockPayloadGenerator.generate(operation)
    );
    expect(router.replace).toHaveBeenCalledWith("/null/");
  });

  it("should have the correct next url", async () => {
    expect.hasAssertions();
    const { router } = useRouter();
    const user = userEvent.setup();
    render(<Login router={router} match={{ params: { next: "search" } }} />);

    const usernameField = screen.getByLabelText("Email");
    const passwordField = screen.getByLabelText("Password");

    await user.type(usernameField, "asher");
    await user.type(passwordField, "password");

    await user.click(screen.getAllByText("Sign in")[1]);
    screen.debug();
    expect(router.replace).toHaveBeenCalledWith("/search/");
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

    await waitFor(() =>
      expect(
        screen.getByText("Please enter valid credentials.")
      ).toBeInTheDocument()
    );
  });
});
