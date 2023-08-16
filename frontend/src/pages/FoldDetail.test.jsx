import { useRouter } from "found";
import FoldDetail from "./FoldDetail";
import { render, screen, waitFor } from "@testing-library/react";
import { RelayEnvironmentProvider } from "react-relay";
import { MockPayloadGenerator, createMockEnvironment } from "relay-test-utils";

describe("fold detail component", () => {
  const mockResizeObserver = () => {
    delete window.ResizeObserver;
    window.ResizeObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
  };

  const cleanupMockResizeObserver = () => {
    window.ResizeObserver = ResizeObserver;
    vi.restoreAllMocks();
  };

  it("should render with the correct title", async () => {
    expect.hasAssertions();
    mockResizeObserver();
    const router = useRouter();
    const environment = createMockEnvironment();
    render(
      <RelayEnvironmentProvider environment={environment}>
        <FoldDetail match={{ params: { jname: "J111-222" } }} router={router} />
      </RelayEnvironmentProvider>
    );

    const mock = {
      FoldPulsarDetailNode() {
        return { ephemeris: '{"Data": {"example": "2", "again": "7"}}' };
      },
    };

    await waitFor(() =>
      environment.mock.resolveMostRecentOperation((operation) =>
        MockPayloadGenerator.generate(operation, mock)
      )
    );

    screen.debug();
    expect(screen.getByText("J111-222")).toBeInTheDocument();
    cleanupMockResizeObserver();
  });
});
