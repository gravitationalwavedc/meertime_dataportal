import { useRouter } from "found";
import SearchmodeDetail from "./SearchmodeDetail";
import { waitFor, render, screen } from "@testing-library/react";
import { RelayEnvironmentProvider } from "react-relay";
import { createMockEnvironment, MockPayloadGenerator } from "relay-test-utils";

describe("searchmode detail component", () => {
  it("should render with the correct title", async () => {
    expect.hasAssertions();
    const router = useRouter();
    const environment = createMockEnvironment();
    render(
      <RelayEnvironmentProvider environment={environment}>
        <SearchmodeDetail
          match={{ params: { jname: "J111-222", project: "meertime" } }}
          router={router}
        />
      </RelayEnvironmentProvider>
    );

    await waitFor(() =>
      environment.mock.resolveMostRecentOperation((operation) =>
        MockPayloadGenerator.generate(operation)
      )
    );
    expect(screen.getByText("J111-222")).toBeInTheDocument();
  });
});
