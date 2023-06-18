import { fireEvent, render, waitFor } from "@testing-library/react";
import DataView from "./DataView";

describe("data view component", () => {
  const rows = [
    {
      band: "L-band",
      beam: 4,
      bw: 856,
      dmFold: 314,
      dmPipe: null,
      id: "T2JzZXJ2YXRpb25EZXRhaWxOb2RlOjE4MDgz",
      key: "2020-09-29-17:13:32:4",
      length: 5,
      nant: 58,
      nantEff: 58,
      nbin: 1024,
      nchan: 1024,
      proposalShort: "TPA",
      rmPipe: null,
      snrPipe: null,
      snrSpip: 38.7,
      utc: "2020-09-29-17:13:32",
    },
  ];

  const columns = [
    { dataField: "key", text: "", sort: false, hidden: true },
    { dataField: "utc", text: "Timestamp", sort: true },
    { dataField: "proposalShort", text: "Project", sort: true },
    { dataField: "length", text: "Length [m]", sort: true },
    { dataField: "beam", text: "Beam", sort: true },
    { dataField: "bw", text: "BW", sort: true },
    { dataField: "nchan", text: "Nchan", sort: true },
    { dataField: "band", text: "Band", sort: true },
    { dataField: "nbin", text: "Nbin", sort: true },
    { dataField: "nant", text: "Nant", sort: true },
    { dataField: "nantEff", text: "Nant eff", sort: true },
    { dataField: "dmFold", text: "DM fold", sort: true },
    { dataField: "dmPipe", text: "DM meerpipe", sort: true },
    { dataField: "rmPipe", text: "RM meerpipe", sort: true },
    { dataField: "snrSpip", text: "S/N backend", sort: true },
    { dataField: "snrPipe", text: "S/N meerpipe", sort: true },
  ];

  const summaryData = [
    { title: "Observations", value: 2 },
    { title: "Projects", value: 2 },
    { title: "Timespan [days]", value: 2 },
    { title: "Hours", value: 2 },
    { title: "Size [MB]", value: 2 },
  ];

  it("should toggle table view when the icon is clicked", async () => {
    expect.hasAssertions();
    const { getByTestId, getAllByTestId, queryByTestId } = render(
      <DataView
        rows={rows}
        columns={columns}
        summaryData={summaryData}
        keyField="key"
      />
    );
    const listViewButton = getByTestId("list-view-button");
    const tableViewButton = getByTestId("table-view-button");
    fireEvent.click(listViewButton);
    await waitFor(() => getByTestId("job-card"));
    expect(getAllByTestId("job-card")[0]).toBeInTheDocument();
    fireEvent.click(tableViewButton);
    expect(queryByTestId("job-card")).toBeNull();
  });
});
