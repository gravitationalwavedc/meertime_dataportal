import { render, screen } from "@testing-library/react";
import ImageComparisonRow from "./ImageComparisonRow";

describe("ImageComparisonRow", () => {
  const openLightBox = () => {};

  it("renders 1 column with PlotImage when only rawImage exists", () => {
    const rawImage = {
      node: { url: "raw.png", imageType: "profile", cleaned: false },
    };
    render(
      <ImageComparisonRow
        rawImage={rawImage}
        processedImage={null}
        openLightBox={openLightBox}
      />
    );

    expect(screen.getByAltText("Plot profile raw")).toBeInTheDocument();
    expect(screen.queryByAltText(/Plot.*cleaned/)).not.toBeInTheDocument();
    expect(screen.queryByTestId("empty-state-message")).not.toBeInTheDocument();
  });

  it("renders 1 column with PlotImage when only processedImage exists", () => {
    const processedImage = {
      node: { url: "cleaned.png", imageType: "profile", cleaned: true },
    };
    render(
      <ImageComparisonRow
        rawImage={null}
        processedImage={processedImage}
        openLightBox={openLightBox}
      />
    );

    expect(screen.getByAltText("Plot profile cleaned")).toBeInTheDocument();
    expect(screen.queryByAltText(/Plot.*raw/)).not.toBeInTheDocument();
    expect(screen.queryByTestId("empty-state-message")).not.toBeInTheDocument();
  });

  it("renders 2 columns with PlotImages when both exist", () => {
    const rawImage = {
      node: { url: "raw.png", imageType: "profile", cleaned: false },
    };
    const processedImage = {
      node: { url: "cleaned.png", imageType: "profile", cleaned: true },
    };
    render(
      <ImageComparisonRow
        rawImage={rawImage}
        processedImage={processedImage}
        openLightBox={openLightBox}
      />
    );

    expect(screen.getByAltText("Plot profile raw")).toBeInTheDocument();
    expect(screen.getByAltText("Plot profile cleaned")).toBeInTheDocument();
    expect(screen.queryByTestId("empty-state-message")).not.toBeInTheDocument();
  });

  it("renders a single column with EmptyStateMessage when neither exists", () => {
    render(
      <ImageComparisonRow
        rawImage={null}
        processedImage={null}
        openLightBox={openLightBox}
      />
    );

    expect(screen.getByTestId("empty-state-message")).toBeInTheDocument();
    expect(screen.getByText("No plot available")).toBeInTheDocument();
  });
});
