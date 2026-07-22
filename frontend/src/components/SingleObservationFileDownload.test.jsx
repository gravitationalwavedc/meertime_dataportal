import { render, screen } from "@testing-library/react";
import SingleObservationFileDownload from "./SingleObservationFileDownload";

const baseProps = {
  jname: "J0125-2327",
  utc: "2024-01-02-03:04:05",
  beam: 1,
  mainProject: "Synthetic",
  isAuthenticated: true,
};

describe("SingleObservationFileDownload", () => {
  it("hides observation download controls when downloads are disabled", () => {
    render(
      <SingleObservationFileDownload {...baseProps} allowDownloads={false} />
    );

    expect(
      screen.queryByRole("button", { name: "Download Full Resolution" })
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Download Decimated" })
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Download ToAs" })
    ).not.toBeInTheDocument();
  });

  it("does not use a MainProject name carve-out when downloads are enabled", () => {
    render(
      <SingleObservationFileDownload
        {...baseProps}
        mainProject="MONSPSR"
        allowDownloads
      />
    );

    expect(
      screen.getByRole("button", { name: "Download Full Resolution" })
    ).toBeInTheDocument();
  });
});
