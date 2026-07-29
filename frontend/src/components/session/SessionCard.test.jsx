import { render, screen } from "@testing-library/react";
import SessionCard from "./SessionCard";

describe("SessionCard", () => {
  it("builds links from the observation MainProject", () => {
    render(
      <SessionCard
        row={{
          jname: "J0125-2327",
          obsType: "fold",
          mainProject: "SyntheticMain",
          utcStart: "2023-04-29T06:47:34+00:00",
          utc: "2023-04-29-06:47:34",
          beam: 2,
        }}
      />
    );

    expect(
      screen.getByRole("link", { name: "View all observations" })
    ).toHaveAttribute("href", "/fold/SyntheticMain/J0125-2327/");
    expect(
      screen.getByRole("link", { name: "View last observation" })
    ).toHaveAttribute(
      "href",
      "/SyntheticMain/J0125-2327/2023-04-29-06:47:34/2/"
    );
  });
});
