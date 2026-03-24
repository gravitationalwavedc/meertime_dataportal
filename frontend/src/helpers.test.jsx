import { kronosLink, toApiFilter } from "./helpers";

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
});
