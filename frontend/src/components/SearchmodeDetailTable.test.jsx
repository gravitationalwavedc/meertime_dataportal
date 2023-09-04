import { fireEvent, render, waitFor } from "@testing-library/react";
import SearchmodeDetailTable from "./SearchmodeDetailTable";

describe("search mode detail table", () => {
  const data = {
    "observationSummary": {
      "edges": [
        {
          "node": {
            "observations": 1,
            "projects": 1,
            "observationHours": 3,
            "timespanDays": 1
          }
        }
      ]
    },
    "observation": {
      "edges": [
        {
          "node": {
            "id": "1",
            "utcStart": "2023-06-27T11:37:31+00:00",
            "raj": "13:26:47.24",
            "decj": "-47:28:46.5",
            "beam": 1,
            "duration": 14399.068999999645,
            "frequency": 1283.89550781,
            "nantEff": 41,
            "filterbankNbit": 8,
            "filterbankNpol": 4,
            "filterbankNchan": 256,
            "filterbankTsamp": 19.14,
            "filterbankDm": 99.9,
            "project": {
              "short": "RelBin"
            },
          }
        },
        {
          "node": {
            "id": "2",
            "utcStart": "2023-06-27T11:37:31+00:00",
            "raj": "13:26:47.24",
            "decj": "-47:28:46.5",
            "beam": 1,
            "duration": 14399.068999999645,
            "frequency": 1283.89550781,
            "nantEff": 41,
            "filterbankNbit": 8,
            "filterbankNpol": 4,
            "filterbankNchan": 256,
            "filterbankTsamp": 19.14,
            "filterbankDm": 99.9,
            "project": {
              "short": "RelBin"
            },
          }
        },
        {
          "node": {
            "id": "3",
            "utcStart": "2023-06-27T11:37:31+00:00",
            "raj": "13:26:47.24",
            "decj": "-47:28:46.5",
            "beam": 1,
            "duration": 14399.068999999645,
            "frequency": 1283.89550781,
            "nantEff": 41,
            "filterbankNbit": 8,
            "filterbankNpol": 4,
            "filterbankNchan": 256,
            "filterbankTsamp": 19.14,
            "filterbankDm": 99.9,
            "project": {
              "short": "TPA"
            },
          }
        },
        {
          "node": {
            "id": "4",
            "utcStart": "2023-06-27T11:37:31+00:00",
            "raj": "13:26:47.24",
            "decj": "-47:28:46.5",
            "beam": 1,
            "duration": 14399.068999999645,
            "frequency": 1283.89550781,
            "nantEff": 41,
            "filterbankNbit": 8,
            "filterbankNpol": 4,
            "filterbankNchan": 256,
            "filterbankTsamp": 19.14,
            "filterbankDm": 99.9,
            "project": {
              "short": "TPA"
            },
          }
        },
      ],
    },
  };

  const mainProject = "MeerTIME";
  it("should render data onto the table", () => {
    expect.hasAssertions();
    const { getByText } = render(<SearchmodeDetailTable data={data} mainProject={mainProject}/>);
    expect(getByText("Observations")).toBeInTheDocument();
    expect(getByText("2023-06-27-11:37:31")).toBeInTheDocument();
  });

  it("should update the table when the project filter is changed", async () => {
    expect.hasAssertions();
    const { getAllByText, getByLabelText } = render(
      <SearchmodeDetailTable data={data} />
    );
    console.log(getAllByText("RelBin"));
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
