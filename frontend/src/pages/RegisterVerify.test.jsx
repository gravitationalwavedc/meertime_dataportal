import RegisterVerify from "./RegisterVerify";
import React from "react";
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

describe("register verify component", () => {
  it("should display the status verifying while waiting for data", () => {
    expect.hasAssertions();
    const { getByText } = render(
      <RegisterVerify match={{ params: { code: "code" } }} />
    );
    expect(getByText("Register")).toBeInTheDocument();
    expect(getByText("Email verification in progress")).toBeInTheDocument();
  });
});
