import React, { useState, useEffect } from 'react';
import { createRefetchContainer, graphql } from 'react-relay';
import { Row, Col, Button } from 'react-bootstrap';
import ListControls from '../components/ListControls';
import BootstrapTable from 'react-bootstrap-table-next';
import paginationFactory from 'react-bootstrap-table2-paginator';
import ToolkitProvider from 'react-bootstrap-table2-toolkit';
import { HiOutlineViewGrid, HiOutlineViewList } from 'react-icons/hi';
import moment from 'moment';
import JobCardsList from './JobCardsList';
import sizePerPageRenderer from './CustomSizePerPageBtn';

const FoldTable = ({ data, relay }) => {
    const [proposal, setProposal] = useState('All');
    const [band, setBand] = useState('All');
    const [isTableView, setIsTableView] = useState(true);

    useEffect(() => {
        relay.refetch({ mode: 'observations', proposal: proposal, band: band });
    }, [proposal, band, relay]);

    const rows = data.foldObservations.edges.reduce((result, edge) => { 
        const row = { ...edge.node };
        row.last = moment.parseZone(row.last, moment.ISO_8601).format('YYYY-MM-DD-HH:mm:ss');
        row.first = moment.parseZone(row.first, moment.ISO_8601).format('YYYY-MM-DD-HH:mm:ss');
        row.totalTintH = `${row.totalTintH} hours`;
        row.latestTintM = `${row.latestTintM} minutes`;
        row.action = <Button size='sm' variant="outline-primary">View details</Button>;
        return [...result, { ...row }];
    }, []);
    
    const columns = [
        { dataField: 'jname', text: 'JName', align: 'center', headerAlign: 'center', sort:true },
        { dataField: 'last', text: 'Last', sort: true },
        { dataField: 'first', text: 'First', sort: true },
        { dataField: 'proposalShort', text: 'Project', sort: true },
        { dataField: 'timespan', text: 'Timespan', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'nobs', text: 'Observations', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'totalTintH', text: 'Total int [h]', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'avgSnr5min', text: 'Avg S/N pipe (5 mins)', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'maxSnr5min', text: 'Max S/N pipe (5 mins)', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'latestSnr', text: 'Last S/N raw', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'latestTintM', text: 'Last int. [m]', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'action', text: '', align: 'center', headerAlign: 'center', sort: false }
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
        lastPageText: 'Last',
        showTotal: true,
        disablePageTitle: true, sizePerPageRenderer,
    };

    return (
        <ToolkitProvider
            bootstrap4 
            keyField='jname' 
            columns={columns} 
            data={rows} 
            columnToggle
            search
            exportCSV
        >
            {props => (
                <React.Fragment>
                    <Row className="justify-content-end" style={{ marginTop: '-5rem' }}>
                        <Col md={1}>
                            <p className="mb-1 text-muted">Observations</p>
                            <h4>{ data.foldObservations.totalObservations }</h4>
                        </Col>
                        <Col md={1}>
                            <p className="mb-1 text-muted">Pulsars</p>
                            <h4>{ data.foldObservations.totalPulsars }</h4>
                        </Col>
                        <Col md={1}>
                            <p className="mb-1 text-muted">Total Hours</p>
                            <h4>{ data.foldObservations.totalObservationTime }</h4>
                        </Col>
                    </Row>
                    <Row>
                        <Col md={3}>
                            <ListControls 
                                searchProps={props.searchProps} 
                                handleProposalFilter={setProposal} 
                                handleBandFilter={setBand}
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
                            /> : 
                            <JobCardsList {...props.baseProps} />
                    }
                </React.Fragment>)}
        </ToolkitProvider>
    );
};

export default createRefetchContainer(
    FoldTable,
    {
        data: graphql`
          fragment FoldTable_data on Query @argumentDefinitions(
            mode: {type: "String", defaultValue: "observations"},
            proposal: {type: "String", defaultValue: "All"}
            band: {type: "String", defaultValue: "All"}
          ) {
            foldObservations(mode: $mode, proposal: $proposal, band: $band) {
              totalObservations
              totalPulsars
              totalObservationTime
              edges {
                node {
                  jname
                  last
                  first
                  proposalShort
                  timespan
                  nobs
                  latestSnr
                  latestTintM
                  maxSnr5min
                  avgSnr5min
                  totalTintH
                }
              }
            }
          }`
    },
    graphql`
      query FoldTableRefetchQuery($mode: String!, $proposal: String, $band: String) {
        ...FoldTable_data @arguments(mode: $mode, proposal: $proposal, band: $band)
      }
   `
);
