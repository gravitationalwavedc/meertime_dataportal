import { MockPayloadGenerator, createMockEnvironment } from "relay-test-utils";
import { QueryRenderer, graphql } from "react-relay";
import SearchTable from "./SearchTable";
import { render, waitFor, screen } from "@testing-library/react";

describe("search table component", () => {
  const environment = createMockEnvironment();
  const TestRenderer = () => (
    <QueryRenderer
      environment={environment}
      query={graphql`
        query SearchTableTestQuery @relay_test_operation {
          ...SearchTable_data
        }
      `}
      render={({ error, props }) => {
        if (props) {
          return <SearchTable data={props} />;
        } else if (error) {
          return error.message;
        }
        return "Loading...";
      }}
    />
  );

  it("should renders the SearchTable with data", async () => {
    expect.hasAssertions();
    render(<TestRenderer />);
    screen.debug();
    await waitFor(() =>
      environment.mock.resolveMostRecentOperation((operation) =>
        MockPayloadGenerator.generate(operation)
      )
    );
    await waitFor(() =>
      expect(screen.getAllByText("Observations")[0]).toBeInTheDocument()
    );
    expect(screen.getAllByText("42")[0]).toBeInTheDocument();
  });
});
