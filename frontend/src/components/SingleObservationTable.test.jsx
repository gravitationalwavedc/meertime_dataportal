import { render, screen } from "@testing-library/react";
import SingleObservationTable from "./SingleObservationTable";

describe("observationTimeView component", () => {
  it("should render the page with images", () => {
    expect.hasAssertions();
    const data = {
      pulsarFoldResult: {
        edges: [
          {
            node: {
              observation: {
                calibration: {
                  id: "Q2FsaWJyYXRpb25Ob2RlOjYyNw==",
                  idInt: 627,
                },
                beam: 4,
                utcStart: "2020-10-06T14:33:16+00:00",
                obsType: "FOLD",
                project: {
                  id: "UHJvamVjdE5vZGU6NA==",
                  short: "RelBin",
                  mainProject: {
                    name: "MeerTIME",
                  },
                },
                frequency: 1283.58203125,
                bandwidth: 856,
                raj: "10:17:51.3284042",
                decj: "-71:56:41.64596",
                duration: 3599.4912287102798,
                foldNbin: 1024,
                foldNchan: 1024,
                foldTsubint: 8,
                nant: 57,
              },
              images: {
                edges: [
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/raw_profile_ftp.png",
                      cleaned: false,
                      imageType: "PROFILE",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/raw_profile_ftp.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/cleaned_profile_ftp.png",
                      cleaned: true,
                      imageType: "PROFILE",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/cleaned_profile_ftp.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/raw_profile_fts.png",
                      cleaned: false,
                      imageType: "PROFILE_POL",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/raw_profile_fts.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/cleaned_profile_fts.png",
                      cleaned: true,
                      imageType: "PROFILE_POL",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/cleaned_profile_fts.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/raw_phase_time.png",
                      cleaned: false,
                      imageType: "PHASE_TIME",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/raw_phase_time.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/cleaned_phase_time.png",
                      cleaned: true,
                      imageType: "PHASE_TIME",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/cleaned_phase_time.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/raw_phase_freq.png",
                      cleaned: false,
                      imageType: "PHASE_FREQ",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/raw_phase_freq.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/cleaned_phase_freq.png",
                      cleaned: true,
                      imageType: "PHASE_FREQ",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/cleaned_phase_freq.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/raw_bandpass.png",
                      cleaned: false,
                      imageType: "BANDPASS",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/raw_bandpass.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/cleaned_bandpass.png",
                      cleaned: true,
                      imageType: "BANDPASS",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/cleaned_bandpass.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/raw_SNR_cumulative.png",
                      cleaned: false,
                      imageType: "SNR_CUMUL",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/raw_SNR_cumulative.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/cleaned_SNR_cumulative.png",
                      cleaned: true,
                      imageType: "SNR_CUMUL",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/cleaned_SNR_cumulative.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/raw_SNR_single.png",
                      cleaned: false,
                      imageType: "SNR_SINGLE",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/raw_SNR_single.png",
                    },
                  },
                  {
                    node: {
                      image:
                        "MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14:33:16/4/cleaned_SNR_single.png",
                      cleaned: true,
                      imageType: "SNR_SINGLE",
                      resolution: "HIGH",
                      url: "/media/MeerKAT/SCI-20180516-MB-03/J1017-7156/2020-10-06-14%3A33%3A16/4/cleaned_SNR_single.png",
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

    expect(getByAltText("Plot PROFILE raw")).toHaveAttribute(
      "src",
      expect.stringContaining("raw_profile_ftp.png")
    );
    expect(getByAltText("Plot PROFILE cleaned")).toHaveAttribute(
      "src",
      expect.stringContaining("cleaned_profile_ftp.png")
    );
    expect(getByAltText("Plot PROFILE_POL raw")).toHaveAttribute(
      "src",
      expect.stringContaining("raw_profile_fts.png")
    );
    expect(getByAltText("Plot PROFILE_POL cleaned")).toHaveAttribute(
      "src",
      expect.stringContaining("cleaned_profile_fts.png")
    );
    expect(getByAltText("Plot PHASE_TIME raw")).toHaveAttribute(
      "src",
      expect.stringContaining("raw_phase_time.png")
    );
    expect(getByAltText("Plot PHASE_TIME cleaned")).toHaveAttribute(
      "src",
      expect.stringContaining("cleaned_phase_time.png")
    );
    expect(getByAltText("Plot PHASE_FREQ raw")).toHaveAttribute(
      "src",
      expect.stringContaining("raw_phase_freq.png")
    );
    expect(getByAltText("Plot PHASE_FREQ cleaned")).toHaveAttribute(
      "src",
      expect.stringContaining("cleaned_phase_freq.png")
    );
    expect(getByAltText("Plot BANDPASS raw")).toHaveAttribute(
      "src",
      expect.stringContaining("raw_bandpass.png")
    );
    expect(getByAltText("Plot BANDPASS cleaned")).toHaveAttribute(
      "src",
      expect.stringContaining("cleaned_bandpass.png")
    );
    expect(getByAltText("Plot SNR_CUMUL raw")).toHaveAttribute(
      "src",
      expect.stringContaining("raw_SNR_cumulative.png")
    );
    expect(getByAltText("Plot SNR_CUMUL cleaned")).toHaveAttribute(
      "src",
      expect.stringContaining("cleaned_SNR_cumulative.png")
    );
    expect(getByAltText("Plot SNR_SINGLE raw")).toHaveAttribute(
      "src",
      expect.stringContaining("raw_SNR_single.png")
    );
    expect(getByAltText("Plot SNR_SINGLE cleaned")).toHaveAttribute(
      "src",
      expect.stringContaining("cleaned_SNR_single.png")
    );
  });

  it("should render the page with no images available", () => {
    expect.hasAssertions();
    const data = {
      pulsarFoldResult: {
        edges: [
          {
            node: {
              observation: {
                calibration: {
                  id: "Q2FsaWJyYXRpb25Ob2RlOjYyNw==",
                  idInt: 627,
                },
                beam: 4,
                utcStart: "2020-10-06T14:33:16+00:00",
                obsType: "FOLD",
                project: {
                  id: "UHJvamVjdE5vZGU6NA==",
                  short: "RelBin",
                  mainProject: {
                    name: "MeerTIME",
                  },
                },
                frequency: 1283.58203125,
                bandwidth: 856,
                raj: "10:17:51.3284042",
                decj: "-71:56:41.64596",
                duration: 3599.4912287102798,
                foldNbin: 1024,
                foldNchan: 1024,
                foldTsubint: 8,
                nant: 57,
              },
              images: {
                edges: [],
              },
            },
          },
        ],
      },
    };
    render(<SingleObservationTable data={data} />);
    expect(screen.getByText("2020-10-06-14:33:16")).toBeInTheDocument();
  });
});
