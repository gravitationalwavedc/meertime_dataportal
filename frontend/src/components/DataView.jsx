import { Col, Row } from "react-bootstrap";
import React, { useState } from "react";

import BootstrapTable from "react-bootstrap-table-next";
import CustomSizePerPageBtn from "./CustomSizePerPageBtn";
import JobCardsList from "./JobCardsList";
import ListControls from "./ListControls";
import SummaryDataRow from "./SummaryDataRow";
import ToolkitProvider from "react-bootstrap-table2-toolkit";
import paginationFactory from "react-bootstrap-table2-paginator";
import { useScreenSize } from "../context/screenSize-context";
import PlotContainer from "./plots/PlotContainer";

const DataView = ({
  summaryData,
  columns,
  rows,
  toaData,
  jname,
  mainProject,
  setMainProject,
  mostCommonProject,
  setMostCommonProject,
  project,
  setProject,
  band,
  setBand,
  urlQuery,
  options,
  plot,
  keyField,
  card,
  query,
  rememberSearch,
}) => {
  const { screenSize } = useScreenSize();
  const [isTableView, setIsTableView] = useState(
    ["md", "lg", "xl", "xxl"].includes(screenSize)
  );
  return (
    <React.Fragment>
      <SummaryDataRow dataPoints={summaryData} />

      <ToolkitProvider
        bootstrap4
        keyField={keyField}
        columns={columns}
        data={rows}
        exportCSV={{
          fileName: "pulsars-data.csv",
          noAutoBOM: false,
          exportAll: false,
          onlyExportFiltered: true,
        }}
        columnToggle
        search
        condensed
      >
        {(props) => {
          return (
            <React.Fragment>
              {plot && (
                <Row className="d-none d-sm-block">
                  <PlotContainer
                    tableData={rows}
                    toaData={toaData}
                    urlQuery={urlQuery}
                    jname={jname}
                    mainProject={mainProject}
                    {...props.baseProps}
                  />
                </Row>
              )}
              <Row className="bg-gray-100">
                <Col lg={10} md={12}>
                  <ListControls
                    query={query}
                    searchProps={props.searchProps}
                    mainProject={mainProject}
                    handleMainProjectFilter={setMainProject}
                    mostCommonProject={mostCommonProject}
                    handleMostCommonProjectFilter={setMostCommonProject}
                    project={project}
                    handleProjectFilter={setProject}
                    band={band}
                    handleBandFilter={setBand}
                    columnToggleProps={props.columnToggleProps}
                    setIsTableView={setIsTableView}
                    isTableView={isTableView}
                    exportCSVProps={props.csvProps}
                    rememberSearch={rememberSearch}
                  />
                </Col>
              </Row>
              {isTableView ? (
                <BootstrapTable
                  {...props.baseProps}
                  pagination={paginationFactory(options)}
                  bordered={false}
                  rowStyle={{ verticalAlign: "middle" }}
                  wrapperClasses="bg-gray-100"
                />
              ) : (
                <JobCardsList
                  {...props.baseProps}
                  mainProject={mainProject}
                  as={card}
                />
              )}
            </React.Fragment>
          );
        }}
      </ToolkitProvider>
    </React.Fragment>
  );
};

DataView.defaultProps = {
  keyField: "jname",
  options: {
    sizePerPage: 200,
    sizePerPageList: [
      { text: "25", value: 25 },
      { text: "50", value: 50 },
      { text: "100", value: 100 },
      { text: "200", value: 200 },
    ],
    firstPageText: "First",
    prePageText: "Back",
    nextPageText: "Next",
    lastPageText: "Last",
    showTotal: true,
    disablePageTitle: true,
    CustomSizePerPageBtn,
  },
  rememberSearch: false,
};

export default DataView;
