import { fireEvent, render } from "@testing-library/react";
import TopNav from "./TopNav";

vi.mock("found", () => ({
  Link: (component) => <div>{component.children}</div>,
  useRouter: () => ({
    router: {
      push: vi.fn(),
      replace: vi.fn(),
      go: vi.fn(),
      createHref: vi.fn(),
      createLocation: vi.fn(),
      isActive: vi.fn(),
      matcher: {
        match: vi.fn(),
        getRoutes: vi.fn(),
        isActive: vi.fn(),
        format: vi.fn(),
      },
      addTransitionHook: vi.fn(),
    },
  }),
}));

describe("top navigation bar", () => {
  it("should clear the session token on logout", () => {
    expect.hasAssertions();

    // We want some things that we can clear during logout.
    localStorage.setItem("jwt", "secretjwt");
    localStorage.setItem("username", "buffy summers");

    const { getByText } = render(<TopNav />);
    const logoutButton = getByText("Log out");

    fireEvent.click(logoutButton);
    expect(localStorage.length).toEqual(0);
  });
});
