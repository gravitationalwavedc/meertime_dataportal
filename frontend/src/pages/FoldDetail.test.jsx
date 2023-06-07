import { useRouter } from "found";
import FoldDetail from "./FoldDetail";
import { render } from "@testing-library/react";

describe("fold detail component", () => {
  it("should render with the correct title", () => {
    const router = useRouter();
    expect.hasAssertions();
    const { getByText } = render(
      <FoldDetail match={{ params: { jname: "J111-222" } }} router={router} />
    );
    expect(getByText("J111-222")).toBeInTheDocument();
  });
});
