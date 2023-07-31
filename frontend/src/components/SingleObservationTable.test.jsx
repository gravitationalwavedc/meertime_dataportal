import { render, screen, waitFor } from "@testing-library/react";
import SingleObservationTable from "./SingleObservationTable";
import * as imageUtils from "../pages/RefreshToken";

vi.mock("../pages/RefreshToken");

describe("observationTimeView component", () => {
  it("should render the page with images", async() => {
    expect.hasAssertions();

    const getImageDataSpy = vi.spyOn(imageUtils, "getImageData");
    const mockImageUrl = "data:image;base64,VGhpcyBpcyBhIHRlc3Qgc3RyaW5nLg==";
    getImageDataSpy.mockResolvedValue(Promise.resolve(mockImageUrl));

    const data = {
      foldObservationDetails: {
        edges: [
          {
            node: {
              beam: 1,
              utc: "2020-02-04T00:21:21+00:00",
              project: "meertime",
              proposal: "SCI-20180516-MB-02",
              frequency: 1283.582031,
              bw: 775.75,
              ra: "14:24:12.76",
              dec: "-55:56:13.9",
              length: 13.4,
              nbin: 1024,
              nchan: 928,
              tsubint: 8,
              nant: 53,
              schedule: "12",
              phaseup: "12",
              id: "Rm9sZFB1bHNhckRldGFpbE5vZGU6OTA3NzY=",
              images: {
                edges: [
                  {
                    node: {
                      plotType: "time",
                      process: "raw",
                      resolution: "hi",
                      url: "phaseVsTime.mock.png",
                    },
                  },
                  {
                    node: {
                      plotType: "profile",
                      process: "raw",
                      resolution: "hi",
                      url: "profile.mock.png",
                    },
                  },
                  {
                    node: {
                      plotType: "phase",
                      process: "raw",
                      resolution: "hi",
                      url: "phaseVsFrequency.mock.png",
                    },
                  },
                ],
              },
            },
          },
        ],
      },
    };

    const { getByAltText } = render(<SingleObservationTable data={data} />);

    await waitFor(() => {
      expect(getImageDataSpy).toHaveBeenCalled();
      expect(getByAltText("Plot profile using raw data.")).toHaveAttribute(
        "src",
        expect.stringContaining("data:image;base64,")
      );
      expect(getByAltText("Plot time using raw data.")).toHaveAttribute(
        "src",
        expect.stringContaining("data:image;base64,")
      );
      expect(getByAltText("Plot phase using raw data.")).toHaveAttribute(
        "src",
        expect.stringContaining("data:image;base64,")
      );
    });
  });

  it("should render the page with no images available", () => {
    expect.hasAssertions();
    const data = {
      foldObservationDetails: {
        edges: [
          {
            node: {
              beam: 1,
              utc: "2020-02-04T00:21:21+00:00",
              proposal: "SCI-20180516-MB-02",
              project: "meertime",
              frequency: 1283.582031,
              bw: 775.75,
              ra: "14:24:12.76",
              dec: "-55:56:13.9",
              length: 13.4,
              nbin: 1024,
              nchan: 928,
              tsubint: 8,
              nant: 53,
              profileHi: null,
              phaseVsTimeHi: "",
              phaseVsFrequencyHi: "",
              bandpassHi: null,
              snrVsTimeHi: "",
              schedule: "12",
              phaseup: "12",
              id: "Rm9sZFB1bHNhckRldGFpbE5vZGU6OTA3NzY=",
              images: {
                edges: [],
              },
            },
          },
        ],
      },
    };
    render(<SingleObservationTable data={data} />);
    expect(screen.getByText("2020-02-04-00:21:21")).toBeInTheDocument();
  });
});