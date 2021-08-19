/* eslint-disable */
import { Col, Row } from 'react-bootstrap';
import React, { useState } from 'react';

import BootstrapTable from 'react-bootstrap-table-next';
import CustomSizePerPageBtn from './CustomSizePerPageBtn';
import JobCardsList from './JobCardsList';
import ListControls from './ListControls';
import PulsarSummaryPlot from './PulsarSummaryPlot';
import SummaryDataRow from './SummaryDataRow';
import ToolkitProvider from 'react-bootstrap-table2-toolkit';
import paginationFactory from 'react-bootstrap-table2-paginator';
import { useScreenSize } from '../context/screenSize-context';

const DataView = ({ 
    summaryData, 
    columns, 
    rows, 
    mainProject,
    project, 
    setProject, 
    setMainProject,
    setBand, 
    options, 
    plot, 
    maxPlotLength,
    minPlotLength,
    keyField,
    card
  }) => {
    const { screenSize } = useScreenSize();
    const [isTableView, setIsTableView] = useState(["md", "lg", "xl", "xxl"].includes(screenSize));
    return (
        <React.Fragment>
            <SummaryDataRow
                dataPoints={summaryData}/>
            <ToolkitProvider
                bootstrap4 
                keyField={keyField}
                columns={columns} 
                data={rows} 
                exportCSV={{
                    fileName: 'pulsars-data.csv',
                    exportAll: false,
                    onlyExportFiltered: true
                }}
                columnToggle
                search
                condensed
            >
                {props => {
                  return (
                    <React.Fragment>
                        {plot && 
                          <Row className="d-none d-sm-block">
                              <Col>
                                  <PulsarSummaryPlot 
                                    {...props.baseProps} 
                                    maxPlotLength={maxPlotLength} 
                                    minPlotLength={minPlotLength} />
                              </Col>
                          </Row>
                        }
                        <Row className='bg-gray-100'>
                            <Col lg={10} md={12}>
                                <ListControls 
                                    searchProps={props.searchProps} 
                                    handleBandFilter={setBand}
                                    handleMainProjectFilter={setMainProject}
                                    handleProjectFilter={setProject}
                                    mainProject={mainProject}
                                    project={project}
                                    columnToggleProps={props.columnToggleProps}
                                    setIsTableView={setIsTableView}
                                    isTableView={isTableView}
                                    exportCSVProps={props.csvProps}
                                />
                            </Col>
                        </Row>
                        {
                            isTableView ? 
                                <BootstrapTable 
                                    {...props.baseProps} 
                                    pagination={paginationFactory(options)} 
                                    bordered={false}
                                    rowStyle={{ whiteSpace: 'pre', verticalAlign: 'middle' }}
                                    wrapperClasses='bg-gray-100'
                                /> : 
                                <JobCardsList {...props.baseProps} as={card} />
                        }
                    </React.Fragment>)}
              }
            </ToolkitProvider>
        </React.Fragment>);
};

DataView.defaultProps = {
    keyField: 'jname',
    options: {
        sizePerPage: 200,
        sizePerPageList: [
            { text: '25', value: 25 },
            { text: '50', value: 50 },
            { text: '100', value: 100 },
            { text: '200', value: 200 }

        ],
        firstPageText: 'First',
        prePageText: 'Back',
        nextPageText: 'Next',
        lastPageText: 'Last',
        showTotal: true,
        disablePageTitle: true, 
        CustomSizePerPageBtn,
    },
};

export default DataView;
