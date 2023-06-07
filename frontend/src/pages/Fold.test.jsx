import Fold from "./Fold";
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

describe("fold component", () => {
  it("should display a loading message while waiting for data", () => {
    expect.hasAssertions();
    const { getByText } = render(<Fold />);
    expect(getByText("Fold Observations")).toBeInTheDocument();
    expect(getByText("Loading...")).toBeInTheDocument();
  });
});
