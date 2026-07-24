import { extendedObservationColumnVisibility } from "./columnVisibility";

describe("FoldDetailTable", () => {
  it("uses project configuration for extended observation column visibility", () => {
    expect(extendedObservationColumnVisibility(false)).toEqual({
      dmFit: false,
      rm: false,
      nant: false,
      nantEff: false,
      band: false,
      dmBackend: false,
    });

    expect(extendedObservationColumnVisibility(true)).toEqual({
      dmFit: true,
      rm: true,
      nant: true,
      nantEff: true,
      band: true,
      dmBackend: true,
    });
  });
});
