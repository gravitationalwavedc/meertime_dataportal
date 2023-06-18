import { fireEvent, render, waitFor } from "@testing-library/react";
import SearchmodeDetailTable from "./SearchmodeDetailTable";

describe("searhmode detail table", () => {
  const data = {
    searchmodeObservationDetails: {
      totalObservations: 1,
      totalProjects: 1,
      totalTimespanDays: 0,
      edges: [
        {
          node: {
            id: "1",
            utc: "2021-03-02T03:34:32+00:00",
            project: "TPA",
            beam: 4,
            length: 4,
            tsamp: 316.8,
            frequency: 0,
            nchan: 1024,
            nbit: 8,
            npol: 4,
            nantEff: 30,
            dm: 38.28,
            ra: "18:29:05.37",
            dec: "-7:34:22.0",
          },
        },
        {
          node: {
            id: "2",
            utc: "2021-02-02T03:34:32+00:00",
            project: "TPA",
            beam: 4,
            length: 4,
            tsamp: 316.8,
            frequency: 0,
            nchan: 1024,
            nbit: 8,
            npol: 4,
            nantEff: 30,
            dm: 38.28,
            ra: "18:29:05.37",
            dec: "-7:34:22.0",
          },
        },
        {
          node: {
            id: "3",
            utc: "2021-01-02T03:34:32+00:00",
            project: "RelBin",
            beam: 4,
            length: 4,
            tsamp: 316.8,
            frequency: 0,
            nchan: 1024,
            nbit: 8,
            npol: 4,
            nantEff: 30,
            dm: 38.28,
            ra: "18:29:05.37",
            dec: "-7:34:22.0",
          },
        },
        {
          node: {
            id: "4",
            utc: "2021-01-11T03:34:32+00:00",
            project: "RelBin",
            beam: 4,
            length: 4,
            tsamp: 316.8,
            frequency: 0,
            nchan: 1024,
            nbit: 8,
            npol: 4,
            nantEff: 30,
            dm: 38.28,
            ra: "18:29:05.37",
            dec: "-7:34:22.0",
          },
        },
      ],
    },
  };

  it("should render data onto the table", () => {
    expect.hasAssertions();
    const { getByText } = render(<SearchmodeDetailTable data={data} />);
    expect(getByText("Observations")).toBeInTheDocument();
    expect(getByText("2021-03-02-03:34:32")).toBeInTheDocument();
  });

  it("should update the table when the project filter is changed", async () => {
    expect.hasAssertions();
    const { getAllByText, getByLabelText } = render(
      <SearchmodeDetailTable data={data} />
    );
    expect(getAllByText("TPA")).toHaveLength(3);
    expect(getAllByText("RelBin")).toHaveLength(3);

    fireEvent.change(getByLabelText("Project"), { target: { value: "TPA" } });
    await waitFor(() => {
      // There should only be 1 left as an option in the dropdown.
      expect(getAllByText("RelBin")).toHaveLength(1);
      expect(getAllByText("TPA")).toHaveLength(3);
    });
    fireEvent.change(getByLabelText("Project"), { target: { value: "All" } });
    await waitFor(() => {
      // There should only be 1 left as an option in the dropdown.
      expect(getAllByText("RelBin")).toHaveLength(3);
      expect(getAllByText("TPA")).toHaveLength(3);
    });
  });
});
