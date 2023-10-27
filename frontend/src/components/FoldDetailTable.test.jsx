import { fireEvent, render, waitFor } from "@testing-library/react";
import FoldDetailTable from "./FoldDetailTable";

describe("the fold table component", () => {
  const { ResizeObserver } = window;

  const mockResizeObserver = () => {
    delete window.ResizeObserver;
    window.ResizeObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
  };

  const cleanupMockResizeObserver = () => {
    window.ResizeObserver = ResizeObserver;
    vi.restoreAllMocks();
  };

  const data = {
    observationSummary: {
      edges: [
        {
          node: {
            observations: 6,
            observationHours: 1,
            projects: 1,
            pulsars: 1,
            estimatedDiskSpaceGb: 2.12890625,
            timespanDays: 265,
            maxDuration: 1023.8803355514026,
            minDuration: 258.8704538317764,
          },
        },
      ],
    },
    pulsarFoldResult: {
      description: null,
      residualEphemeris: {
        ephemerisData:
          '"{\\"PSRJ\\": \\"J1537+1155\\", \\"RAJ\\": \\"15:37:09.961730\\", \\"RAJ_ERR\\": \\"0.00000300000000000000\\", \\"DECJ\\": \\"+11:55:55.43387\\", \\"DECJ_ERR\\": \\"0.00006000000000000000\\", \\"F0\\": \\"26.382132776893970001\\", \\"F0_ERR\\": \\"1.1e-13\\", \\"F1\\": \\"-1.686097e-15\\", \\"F1_ERR\\": \\"2e-21\\", \\"F2\\": \\"1.7e-29\\", \\"F2_ERR\\": \\"1.1e-30\\", \\"PEPOCH\\": \\"52077\\", \\"POSEPOCH\\": \\"52077\\", \\"DMEPOCH\\": \\"58605.610306199996558\\", \\"DM\\": \\"11.613633504474631914\\", \\"DM_ERR\\": \\"0.00578854674013626249\\", \\"PMRA\\": \\"1.482\\", \\"PMRA_ERR\\": \\"0.00700000000000000000\\", \\"PMDEC\\": \\"-25.285\\", \\"PMDEC_ERR\\": \\"0.01200000000000000000\\", \\"PX\\": \\"0.86000000000000000001\\", \\"PX_ERR\\": \\"0.18000000000000000001\\", \\"SINI\\": \\"0.97719999999999999999\\", \\"SINI_ERR\\": \\"0.00160000000000000000\\", \\"BINARY\\": \\"DD\\", \\"PB\\": \\"0.420737298879\\", \\"PB_ERR\\": \\"0.00000000000200000000\\", \\"T0\\": \\"52076.827113263000001\\", \\"T0_ERR\\": \\"0.00000001100000000000\\", \\"A1\\": \\"3.7294636\\", \\"A1_ERR\\": \\"0.00000060000000000000\\", \\"OM\\": \\"283.30601200000000001\\", \\"OM_ERR\\": \\"0.00001200000000000000\\", \\"ECC\\": \\"0.27367752\\", \\"ECC_ERR\\": \\"0.00000007000000000000\\", \\"PBDOT\\": \\"-1.366e-13\\", \\"PBDOT_ERR\\": \\"2.9999999999999999999e-16\\", \\"OMDOT\\": \\"1.755795\\", \\"OMDOT_ERR\\": \\"0.00000190000000000000\\", \\"M2\\": \\"1.35\\", \\"M2_ERR\\": \\"0.05000000000000000000\\", \\"GAMMA\\": \\"0.0020708000000000000001\\", \\"GAMMA_ERR\\": \\"0.00000050000000000000\\", \\"START\\": \\"2020-04-23T23:32:52.248106Z\\", \\"FINISH\\": \\"2020-09-04T16:34:57.466691Z\\", \\"TZRMJD\\": \\"59000.781389930187444\\", \\"TZRFRQ\\": \\"1076.2680000000000291\\", \\"TZRSITE\\": \\"meerkat\\", \\"TRES\\": \\"80.070\\", \\"EPHVER\\": \\"5\\", \\"CLK\\": \\"TT(TAI)\\", \\"UNITS\\": \\"TDB\\", \\"TIMEEPH\\": \\"IF99\\", \\"DILATEFREQ\\": \\"Y\\", \\"PLANET_SHAPIRO\\": \\"Y\\", \\"T2CMETHOD\\": \\"TEMPO\\", \\"NE_SW\\": \\"4.000\\", \\"CORRECT_TROPOSPHERE\\": \\"N\\", \\"EPHEM\\": \\"DE405\\", \\"NITS\\": \\"1\\", \\"NTOA\\": \\"179\\", \\"CHI2R\\": \\"0.0000\\", \\"CHI2R_ERR\\": \\"177\\", \\"TIMEOFFSETS\\": [{\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58550_58690_1K\\", \\"display\\": \\"-0.000306243\\", \\"offset\\": \\"-0.000306243\\", \\"fit\\": \\"-0.000306243\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58526.21089_1K\\", \\"display\\": \\"-2.4628e-05\\", \\"offset\\": \\"-2.4628e-05\\", \\"fit\\": \\"-2.4628e-05\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58550.14921_1K\\", \\"display\\": \\"2.463e-05\\", \\"offset\\": \\"2.463e-05\\", \\"fit\\": \\"2.463e-05\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58550.14921B_1K\\", \\"display\\": \\"-1.196e-06\\", \\"offset\\": \\"-1.196e-06\\", \\"fit\\": \\"-1.196e-06\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58557.14847_1K\\", \\"display\\": \\"-4.785e-06\\", \\"offset\\": \\"-4.785e-06\\", \\"fit\\": \\"-4.785e-06\\"}, {\\"type\\": \\"JUMP\\", \\"mjd\\": \\"-MJD_58575.9591_1K\\", \\"display\\": \\"5.981308411e-07\\", \\"offset\\": \\"5.981308411e-07\\", \\"fit\\": \\"5.981308411e-07\\"}], \\"P0\\": 0.0379044411783046, \\"P0_ERR\\": 2e-16}"',
        createdAt: "2023-08-22T08:48:08.580310+00:00",
      },
      toasLink: null,
      edges: [
        {
          node: {
            observation: {
              utcStart: "2020-04-23T23:30:43+00:00",
              duration: 258.8704538317764,
              beam: 2,
              bandwidth: 856,
              nchan: 1024,
              band: "UHF",
              foldNbin: 1024,
              nant: 58,
              nantEff: 58,
              project: {
                short: "PTA",
              },
              ephemeris: {
                dm: 11.712308,
              },
            },
            pipelineRun: {
              dm: null,
              dmErr: null,
              rm: null,
              rmErr: null,
              sn: 13.3218755722046,
              flux: 0.118,
              toas: {
                edges: [
                  {
                    node: {
                      freqMhz: 1292.608,
                      mjd: "58962.981155104556",
                      mjdErr: 63.694,
                      length: 248,
                      residual: null,
                    },
                  },
                ],
              },
            },
          },
        },
        {
          node: {
            observation: {
              utcStart: "2020-05-31T18:36:41+00:00",
              duration: 1023.8803355514026,
              beam: 3,
              bandwidth: 856,
              nchan: 1024,
              band: "UHF",
              foldNbin: 1024,
              nant: 59,
              nantEff: 59,
              project: {
                short: "PTA",
              },
              ephemeris: {
                dm: 11.712308,
              },
            },
            pipelineRun: {
              dm: 12.020961375039974,
              dmErr: 0.143431562802167,
              rm: 7.4324,
              rmErr: 0.9,
              sn: 69.2035827636719,
              flux: 0.236,
              toas: {
                edges: [
                  {
                    node: {
                      freqMhz: 1292.112,
                      mjd: "59000.781428808986",
                      mjdErr: 11.224,
                      length: 1016,
                      residual: {
                        mjd: "59000.786906747273",
                        residualSec: 0.00005389760018555287,
                        residualSecErr: 1.1224e-8,
                        residualPhase: 0.001421933644451201,
                        residualPhaseErr: 2.9611305828785816e-7,
                      },
                    },
                  },
                ],
              },
            },
          },
        },
        {
          node: {
            observation: {
              utcStart: "2020-08-21T16:23:38+00:00",
              duration: 1023.5667235887857,
              beam: 2,
              bandwidth: 856,
              nchan: 1024,
              band: "UHF",
              foldNbin: 1024,
              nant: 57,
              nantEff: 57,
              project: {
                short: "PTA",
              },
              ephemeris: {
                dm: 11.712308,
              },
            },
            pipelineRun: {
              dm: 11.66726078669685,
              dmErr: 0.08598996099484987,
              rm: 6.81953,
              rmErr: 0.74,
              sn: 146.669036865234,
              flux: 0.475,
              toas: {
                edges: [
                  {
                    node: {
                      freqMhz: 1288.663,
                      mjd: "59082.689040313603",
                      mjdErr: 6.365,
                      length: 1016,
                      residual: {
                        mjd: "59082.688939251106",
                        residualSec: -0.00009351121332260817,
                        residualSecErr: 6.365e-9,
                        residualPhase: -0.0024670252460055053,
                        residualPhaseErr: 1.6792227512493027e-7,
                      },
                    },
                  },
                ],
              },
            },
          },
        },
        {
          node: {
            observation: {
              utcStart: "2020-08-27T14:38:29+00:00",
              duration: 511.62547439252404,
              beam: 2,
              bandwidth: 856,
              nchan: 1024,
              band: "LBAND",
              foldNbin: 1024,
              nant: 56,
              nantEff: 56,
              project: {
                short: "PTA",
              },
              ephemeris: {
                dm: 11.712308,
              },
            },
            pipelineRun: {
              dm: 11.02358500241079,
              dmErr: 0.13344008514509687,
              rm: 10.6533,
              rmErr: 0.47,
              sn: 128.509460449219,
              flux: 0.636,
              toas: {
                edges: [
                  {
                    node: {
                      freqMhz: 1284.899,
                      mjd: "59088.612968119294",
                      mjdErr: 6.771,
                      length: 504,
                      residual: {
                        mjd: "59088.612379772593",
                        residualSec: -0.0000010044731334087886,
                        residualSecErr: 6.771e-9,
                        residualPhase: -0.000026500143576413393,
                        residualPhaseErr: 1.7863342103234922e-7,
                      },
                    },
                  },
                ],
              },
            },
          },
        },
        {
          node: {
            observation: {
              utcStart: "2020-09-04T16:30:43+00:00",
              duration: 511.6254743925241,
              beam: 2,
              bandwidth: 856,
              nchan: 1024,
              band: "LBAND",
              foldNbin: 1024,
              nant: 58,
              nantEff: 58,
              project: {
                short: "PTA",
              },
              ephemeris: {
                dm: 11.712308,
              },
            },
            pipelineRun: {
              dm: 12.751866886689957,
              dmErr: 0.11804132586725946,
              rm: 6.51518,
              rmErr: 1.4,
              sn: 145.390823364258,
              flux: 0.689,
              toas: {
                edges: [
                  {
                    node: {
                      freqMhz: 1298.808,
                      mjd: "59096.690975572331",
                      mjdErr: 6.103,
                      length: 504,
                      residual: {
                        mjd: "59096.689746419255",
                        residualSec: -0.00005288027959919684,
                        residualSecErr: 6.103e-9,
                        residualPhase: -0.0013950945576652884,
                        residualPhaseErr: 1.6101015633738402e-7,
                      },
                    },
                  },
                ],
              },
            },
          },
        },
        {
          node: {
            observation: {
              utcStart: "2021-01-13T04:32:37+00:00",
              duration: 1022.5469440000007,
              beam: 1,
              bandwidth: 856,
              nchan: 1024,
              band: "LBAND",
              foldNbin: 1024,
              nant: 63,
              nantEff: 63,
              project: {
                short: "PTA",
              },
              ephemeris: {
                dm: 11.712308,
              },
            },
            pipelineRun: {
              dm: 12.400712200627792,
              dmErr: 0.06008066107180355,
              rm: 5.4226,
              rmErr: 1,
              sn: 457.906158447266,
              flux: 1.229,
              toas: {
                edges: [
                  {
                    node: {
                      freqMhz: 1284.629,
                      mjd: "59227.195245731400",
                      mjdErr: 3.905,
                      length: 1016,
                      residual: {
                        mjd: "59227.193926988734",
                        residualSec: 0.000046032533123258094,
                        residualSecErr: 3.905e-9,
                        residualPhase: 0.0012144364009145647,
                        residualPhaseErr: 1.0302222849377104e-7,
                      },
                    },
                  },
                ],
              },
            },
          },
        },
      ],
    },
  };

  const dataNoEphemeris = {
    observationSummary: {
      edges: [
        {
          node: {
            observations: 6,
            observationHours: 1,
            projects: 1,
            pulsars: 1,
            estimatedDiskSpaceGb: 2.12890625,
            timespanDays: 265,
            maxDuration: 1023.8803355514026,
            minDuration: 258.8704538317764,
          },
        },
      ],
    },
    pulsarFoldResult: {
      description: null,
      residualEphemeris: {
        ephemerisData: null,
        createdAt: null,
      },
      toasLink: null,
      edges: [
        {
          node: {
            observation: {
              utcStart: "2020-04-23T23:30:43+00:00",
              duration: 258.8704538317764,
              beam: 2,
              bandwidth: 856,
              nchan: 1024,
              band: "UHF",
              foldNbin: 1024,
              nant: 58,
              nantEff: 58,
              project: {
                short: "PTA",
              },
              ephemeris: {
                dm: 11.712308,
              },
            },
            pipelineRun: {
              dm: null,
              dmErr: null,
              rm: null,
              rmErr: null,
              sn: 13.3218755722046,
              flux: 0.118,
              toas: {
                edges: [
                  {
                    node: {
                      freqMhz: 1292.608,
                      mjd: "58962.981155104556",
                      mjdErr: 63.694,
                      length: 248,
                      residual: null,
                    },
                  },
                ],
              },
            },
          },
        },
      ],
    },
  };

  it("should render data onto the table", () => {
    expect.hasAssertions();
    mockResizeObserver();
    const { getByText, getAllByText } = render(<FoldDetailTable data={data} />);
    expect(getByText("Observations")).toBeInTheDocument();
    expect(
      getByText(
        "Drag to zoom, click empty area to reset, double click to view utc."
      )
    ).toBeInTheDocument();
    expect(getAllByText("PTA")).toHaveLength(1);
    cleanupMockResizeObserver();
  });

  it("should update the table when the band filter is changed", async () => {
    expect.hasAssertions();
    mockResizeObserver();
    const { queryByText, getAllByText, getByLabelText } = render(
      <FoldDetailTable data={data} jname="J123-123" />
    );
    const bandFilter = getByLabelText("Band");
    expect(getAllByText("UHF")).toHaveLength(4);
    expect(getAllByText("LBAND")).toHaveLength(3);

    fireEvent.change(bandFilter, { target: { value: "UHF" } });
    expect(queryByText("LBAND")).not.toBeInTheDocument();

    fireEvent.change(bandFilter, { target: { value: "All" } });
    await waitFor(() => {
      // There should only be 1 left as an option in the dropdown.
      expect(getAllByText("UHF")).toHaveLength(4);
      expect(getAllByText("LBAND")).toHaveLength(3);
    });
    cleanupMockResizeObserver();
  });

  it("should disable the view ephemeris button if the data is missing", () => {
    expect.hasAssertions();
    mockResizeObserver();
    const { getByText } = render(<FoldDetailTable data={dataNoEphemeris} />);
    expect(getByText("Folding ephemeris unavailable")).toBeDisabled();
    cleanupMockResizeObserver();
  });

  it("should toggle the ephemeris modal", () => {
    expect.hasAssertions();
    mockResizeObserver();
    const { getByText, queryByRole } = render(<FoldDetailTable data={data} />);
    const toggleEphemerisButton = getByText("View folding ephemeris");
    expect(queryByRole("dialog")).not.toBeInTheDocument();
    fireEvent.click(toggleEphemerisButton);
    expect(queryByRole("dialog")).toBeInTheDocument();
    cleanupMockResizeObserver();
  });
});
