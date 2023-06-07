import { useRouter } from "found";
import SearchmodeDetail from "./SearchmodeDetail";
import { render } from "@testing-library/react";

describe("searchmode detail component", () => {
  it("should render with the correct title", () => {
    const router = useRouter();
    expect.hasAssertions();
    const { getByText } = render(
      <SearchmodeDetail
        match={{ params: { jname: "J111-222", project: "meertime" } }}
        router={router}
      />
    );
    expect(getByText("J111-222")).toBeInTheDocument();
  });
});
