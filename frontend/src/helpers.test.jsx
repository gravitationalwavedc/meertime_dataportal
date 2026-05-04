import {
  kronosLink,
  selectCanonicalObservationSummaryNode,
  toApiFilter,
} from "./helpers";

describe("how we generated the kronos link", () => {
  it("should create a well formed url", () => {
    expect.hasAssertions();
    const jname = "j1111-2222";
    const beams = 4;
    const utc = "2020-01-01-0:00:00";
    expect(kronosLink(beams, jname, utc)).toBe(
      `http://astronomy.swin.edu.au/pulsar/kronos/utc_start.php?beam=${beams}&utc_start=${utc}&jname=${jname}&data=undefined`
    );
  });

  it("should change All to an empty string", () => {
    expect.hasAssertions();
    expect(toApiFilter("All")).toBe("");
    expect(toApiFilter("PTA")).toBe("PTA");
  });

  it("should handle null and undefined gracefully", () => {
    expect.hasAssertions();
    expect(toApiFilter(null)).toBe("");
    expect(toApiFilter(undefined)).toBe("");
  });

  it("should not double-convert empty strings", () => {
    expect.hasAssertions();
    expect(toApiFilter("")).toBe("");
    expect(toApiFilter(toApiFilter("All"))).toBe("");
  });

  it("should choose aggregate summary node when first edge is narrower", () => {
    expect.hasAssertions();
    const observationSummary = {
      edges: [
        {
          node: {
            observations: 2,
            projects: 1,
            pulsars: 1,
            observationHours: 0,
          },
        },
        {
          node: {
            observations: 5,
            projects: 3,
            pulsars: 2,
            observationHours: 12,
          },
        },
      ],
    };
    expect(selectCanonicalObservationSummaryNode(observationSummary)).toEqual(
      observationSummary.edges[1].node
    );
  });

  it("should keep first node when summary ranking is tied", () => {
    expect.hasAssertions();
    const firstNode = {
      observations: 3,
      projects: 1,
      pulsars: 1,
      observationHours: 4,
    };
    const secondNode = {
      observations: 3,
      projects: 1,
      pulsars: 1,
      observationHours: 4,
    };
    const observationSummary = {
      edges: [{ node: firstNode }, { node: secondNode }],
    };
    expect(selectCanonicalObservationSummaryNode(observationSummary)).toBe(
      firstNode
    );
  });

  it("should return null for empty or malformed observation summary", () => {
    expect.hasAssertions();
    expect(selectCanonicalObservationSummaryNode({ edges: [] })).toBeNull();
    expect(selectCanonicalObservationSummaryNode(null)).toBeNull();
    expect(
      selectCanonicalObservationSummaryNode({ edges: [{}, { node: null }] })
    ).toBeNull();
  });
});
