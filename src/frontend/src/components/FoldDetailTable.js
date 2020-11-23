import { Button, Col, Row } from 'react-bootstrap';
import { HiOutlineViewGrid, HiOutlineViewList } from 'react-icons/hi';
import React, { useState } from 'react';

import BootstrapTable from 'react-bootstrap-table-next';
import DataDisplay from './DataDisplay';
import Einstein from '../assets/images/einstein-coloured.png';
import JobCardsList from './JobCardsList';
import ListControls from '../components/ListControls';
import PulsarSummaryPlot from './PulsarSummaryPlot';
import ToolkitProvider from 'react-bootstrap-table2-toolkit';
import paginationFactory from 'react-bootstrap-table2-paginator';
import sizePerPageRenderer from './CustomSizePerPageBtn';

const FoldDetailTable = ({ data }) => {
    const allRows = data.foldObservationDetails.edges.reduce((result, edge) => [...result, { ...edge.node }], []);
    const [isTableView, setIsTableView] = useState(true);
    const [rows, setRows] = useState(allRows);

    const fit10 = { width: '10%', whiteSpace: 'nowrap' };
    
    const columns = [
        { dataField: 'utc', text: 'Timestamp', sort: true, headerStyle: fit10 },
        { dataField: 'proposalShort', text: 'Project', sort: true },
        { dataField: 'length', text: 'Length [m]', sort: true },
        { dataField: 'beam', text: 'Beam', sort: true },
        { dataField: 'bw', text: 'BW', sort: true },
        { dataField: 'nchan', text: 'Nchan', sort: true },
        { dataField: 'band', text: 'Band', sort: true },
        { dataField: 'nbin', text: 'Nbin', sort: true },
        { dataField: 'nant', text: 'Nant', sort: true },
        { dataField: 'nantEff', text: 'Nant eff', sort: true },
        { dataField: 'dmFold', text: 'DM fold', sort: true },
        { dataField: 'dmPipe', text: 'DM meerpipe', sort: true },
        { dataField: 'rmPipe', text: 'RM meerpipe', sort: true },
        { dataField: 'snrSpip', text: 'S/N backend', sort: true },
        { dataField: 'snrPipe', text: 'S/N meerpipe', sort: true },
    ];

    const options = {
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
        lastPageText: 'Last', showTotal: true,
        disablePageTitle: true, sizePerPageRenderer,
    };

    // totalEstimatedDiskSpace is a human readable formatted byte string in the form of "900.2\u00a0MB".
    // We split on this character so we can use the number and the units separately.
    const [size, sizeFormat] = data.foldObservationDetails.totalEstimatedDiskSpace.split('\u00a0');

    const handleBandFilter = (band) => {
        if(band === 'All') {
            setRows(allRows);
            return;
        }

        const newRows = allRows.filter((row) => row.band === band);
        setRows(newRows);
    };

    const handleProjectFilter = (project) => {
        if(project === 'All') {
            setRows(allRows);
            return;
        }

        const newRows = allRows.filter((row) => row.proposalShort === project);
        setRows(newRows);

    };

    return (
        <ToolkitProvider
            bootstrap4 
            keyField='id' 
            columns={columns} 
            data={rows} 
            columnToggle
            search
            exportCSV
        >
            {props => (
                <React.Fragment>
                    <Row className="justify-content-end" style={{ marginTop: '-9rem' }}>
                        <DataDisplay title="Observations" value={data.foldObservationDetails.totalObservations} />
                        <DataDisplay title="Projects" value={data.foldObservationDetails.totalProjects} />
                        <DataDisplay 
                            title="Timespan [days]" 
                            value={data.foldObservationDetails.totalTimespanDays} />
                        <DataDisplay title="Hours" value={data.foldObservationDetails.totalObservationHours} />
                        <DataDisplay title={`Size [${sizeFormat}]`} value={size} />
                        <img src={Einstein} style={{ marginTop: '-2rem' }} alt=""/>
                    </Row>
                    <Row>
                        <Col>
                            <PulsarSummaryPlot {...props.baseProps}/>
                        </Col>
                    </Row>
                    <Row className='bg-gray-100' style={{ marginTop: '-4rem' }}>
                        <Col md={4}>
                            <ListControls 
                                searchProps={props.searchProps} 
                                searchText="Find an observation..."
                                handleProposalFilter={handleProjectFilter} 
                                handleBandFilter={handleBandFilter}
                                columnToggleProps={props.columnToggleProps}
                                exportCSVProps={props.csvProps}
                            />
                        </Col>
                        <Col md={1} className="d-flex align-items-center">
                            <Button 
                                variant="icon" 
                                className="mr-2" 
                                active={isTableView} 
                                onClick={() => setIsTableView(true)}>
                                <HiOutlineViewList className='h5' />
                            </Button>
                            <Button 
                                variant="icon"
                                active={!isTableView}
                                onClick={() => setIsTableView(false)}>
                                <HiOutlineViewGrid className='h5' />
                            </Button>
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
    );
};

export default FoldDetailTable;
