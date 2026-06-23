import { render, screen } from "@testing-library/react";
import ComparisonImageGrid from "./ComparisonImageGrid";

describe("ComparisonImageGrid", () => {
  const openLightBox = () => {};

  it("renders both Raw and Cleaned headers when both raw and processed images exist", () => {
    const rawImages = [
      { node: { url: "raw.png", imageType: "profile", cleaned: false } },
    ];
    const processedImages = [
      { node: { url: "cleaned.png", imageType: "profile", cleaned: true } },
    ];

    render(
      <ComparisonImageGrid
        rawImages={rawImages}
        processedImages={processedImages}
        openLightBox={openLightBox}
      />
    );

    expect(screen.getByText("Raw")).toBeInTheDocument();
    expect(screen.getAllByText("Cleaned").length).toBeGreaterThan(0);
  });

  it("renders only Raw header when only raw images exist", () => {
    const rawImages = [
      { node: { url: "raw.png", imageType: "profile", cleaned: false } },
    ];
    const processedImages = [];

    render(
      <ComparisonImageGrid
        rawImages={rawImages}
        processedImages={processedImages}
        openLightBox={openLightBox}
      />
    );

    expect(screen.getByText("Raw")).toBeInTheDocument();
    expect(screen.queryByText("Cleaned")).not.toBeInTheDocument();
  });

  it("renders only Cleaned header when only processed images exist", () => {
    const rawImages = [];
    const processedImages = [
      { node: { url: "cleaned.png", imageType: "profile", cleaned: true } },
    ];

    render(
      <ComparisonImageGrid
        rawImages={rawImages}
        processedImages={processedImages}
        openLightBox={openLightBox}
      />
    );

    expect(screen.queryByText("Raw")).not.toBeInTheDocument();
    expect(screen.getAllByText("Cleaned").length).toBeGreaterThan(0);
  });

  it("renders neither header when neither exists", () => {
    const rawImages = [];
    const processedImages = [];

    render(
      <ComparisonImageGrid
        rawImages={rawImages}
        processedImages={processedImages}
        openLightBox={openLightBox}
      />
    );

    expect(screen.queryByText("Raw")).not.toBeInTheDocument();
    expect(screen.queryByText("Cleaned")).not.toBeInTheDocument();
  });
});
