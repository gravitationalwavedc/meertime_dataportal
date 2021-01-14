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

const DataView = ({ summaryData, columns, rows, project, setProject, setProposal, setBand, options, plot, keyField }) => {
    const [isTableView, setIsTableView] = useState(true);

    return (
        <React.Fragment>
            <SummaryDataRow
                dataPoints={summaryData}/>
            <ToolkitProvider
                bootstrap4 
                keyField={keyField}
                columns={columns} 
                data={rows} 
                columnToggle
                search
                exportCSV
            >
                {props => (
                    <React.Fragment>
                        {plot && 
                          <Row>
                              <Col>
                                  <PulsarSummaryPlot {...props.baseProps}/>
                              </Col>
                          </Row>
                        }
                        <Row className='bg-gray-100'>
                            <Col md={6}>
                                <ListControls 
                                    searchProps={props.searchProps} 
                                    handleProposalFilter={setProposal} 
                                    handleBandFilter={setBand}
                                    handleProjectFilter={setProject}
                                    currentProject={project}
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
                                <JobCardsList {...props.baseProps} />
                        }
                    </React.Fragment>)}
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
    }
};

export default DataView;
