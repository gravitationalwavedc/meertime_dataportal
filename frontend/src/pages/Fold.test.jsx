import Fold from "./Fold";
import { render, screen } from "@testing-library/react";
import { createMockEnvironment } from "relay-test-utils";
import { RelayEnvironmentProvider } from "react-relay";

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

const match = {
  location: {
    query: undefined,
  },
};

describe("fold component", () => {
  it("should display a loading message while waiting for data", () => {
    expect.hasAssertions();
    const environment = createMockEnvironment();
    render(
      <RelayEnvironmentProvider environment={environment}>
        <Fold match={match} />
      </RelayEnvironmentProvider>
    );
    expect(screen.getByText("Fold Observations")).toBeInTheDocument();
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });
});
