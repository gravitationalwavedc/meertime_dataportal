import React from "react";
import Register from "./Register";
import { render } from "@testing-library/react";

/* eslint-disable react/display-name */

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

describe("register page", () => {
  it("should have first name, last name, email, and password fields", () => {
    expect.hasAssertions();
    const { getByLabelText } = render(<Register router={{}} match={{}} />);
    expect(getByLabelText("First Name")).toBeInTheDocument();
    expect(getByLabelText("Last Name")).toBeInTheDocument();
    expect(getByLabelText("Email")).toBeInTheDocument();
    expect(getByLabelText("Password")).toBeInTheDocument();
  });
});
