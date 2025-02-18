import { calculatewRMS } from "./plotData";

describe("calculate RMS function", () => {
  it("should return the correct band calculation", () => {
    expect.hasAssertions();
    const data = [
      {
        band: "LBAND",
        error: 0.0013,
        value: -0.005,
      },
      {
        band: "LBAND",
        error: 0.03,
        value: -0.006,
      },
      {
        band: "UHF",
        error: 0.02,
        value: -0.02,
      },
      {
        band: "UHF",
        error: 0.4,
        value: -0.04,
      },
    ];
    const result = calculatewRMS(data);
    const expected = {
      LBAND: 0.00004325211547205803,
      UHF: 0.000997506234413965,
    };
    expect(result).toEqual(expected);
  });

  it("should work when there's no data", () => {
    const data = [];
    const result = calculatewRMS(data);
    expect(result).toEqual({});
  });
});
