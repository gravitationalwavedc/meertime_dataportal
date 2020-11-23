import { Button, ButtonGroup, Col, Row } from 'react-bootstrap';
import { HiOutlineViewGrid, HiOutlineViewList } from 'react-icons/hi';
import React, { useEffect, useState } from 'react';
import { createRefetchContainer, graphql } from 'react-relay';

import BootstrapTable from 'react-bootstrap-table-next';
import Einstein from '../assets/images/einstein-coloured.png';
import JobCardsList from './JobCardsList';
import Link from 'found/Link';
import ListControls from '../components/ListControls';
import ToolkitProvider from 'react-bootstrap-table2-toolkit';
import moment from 'moment';
import paginationFactory from 'react-bootstrap-table2-paginator';
import sizePerPageRenderer from './CustomSizePerPageBtn';

const SearchTable = ({ data, relay }) => {
    const [proposal, setProposal] = useState('All');
    const [band, setBand] = useState('All');
    const [isTableView, setIsTableView] = useState(true);

    useEffect(() => {
        relay.refetch({ mode: 'searchmode', proposal: proposal, band: band });
    }, [proposal, band, relay]);

    const rows = data.relayObservations.edges.reduce((result, edge) => { 
        const row = { ...edge.node };
        row.last = moment.parseZone(row.last, moment.ISO_8601).format('YYYY-MM-DD-HH:mm:ss');
        row.first = moment.parseZone(row.first, moment.ISO_8601).format('YYYY-MM-DD-HH:mm:ss');
        row.totalTintH = `${row.totalTintH} hours`;
        row.latestTintM = `${row.latestTintM} minutes`;
        row.action = <ButtonGroup vertical>
            <Link to={`/search/${row.jname}/`} size='sm' variant="outline-secondary" as={Button}>View all</Link>
            <Button size='sm' variant="outline-secondary">View last</Button>
        </ButtonGroup>;
        return [...result, { ...row }]; }, []);

    const fit2 = { width: '2%', whiteSpace: 'nowrap' };
    const fit6 = { width: '6%', whiteSpace: 'nowrap' };
    const fit8 = { width: '8%', whiteSpace: 'nowrap' };
    
    const columns = [
        { dataField: 'jname', text: 'JName', sort:true, style: fit6, headerStyle: fit6 },
        { dataField: 'last', text: 'Last', sort: true },
        { dataField: 'first', text: 'First', sort: true },
        { dataField: 'proposalShort', text: 'Project', sort: true, style: fit2, headerStyle: fit2 },
        { dataField: 'timespan', text: 'Timespan', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'nobs', text: 'Observations', align: 'right', headerAlign: 'right', 
            sort: true, headerStyle: fit8, style: fit8 },
        { dataField: 'action', text: '', align: 'center', headerAlign: 'center', 
            sort: false, headerStyle: fit8, style: fit8 }
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
                    <Row className="justify-content-end" style={{ marginTop: '-9rem' }}>
                        <Col md={1}>
                            <p className="mb-1 text-primary-600">Observations</p>
                            <h4>{ data.relayObservations.totalObservations }</h4>
                        </Col>
                        <Col md={1}>
                            <p className="mb-1 text-primary-600">Pulsars</p>
                            <h4>{ data.relayObservations.totalPulsars }</h4>
                        </Col>
                        <img src={Einstein} style={{ marginTop: '-2rem' }} alt=""/>
                    </Row>
                    <Row className='bg-gray-100' style={{ marginTop: '-4rem' }}>
                        <Col md={4}>
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
                                wrapperClasses='bg-gray-100'
                            /> : 
                            <JobCardsList {...props.baseProps} />
                    }
                </React.Fragment>)}
        </ToolkitProvider>
    );
};

export default createRefetchContainer(
    SearchTable,
    {
        data: graphql`
          fragment SearchTable_data on Query @argumentDefinitions(
            mode: {type: "String", defaultValue: "searchmode"},
            proposal: {type: "String", defaultValue: "All"}
            band: {type: "String", defaultValue: "All"}
          ) {
            relayObservations(mode: $mode, proposal: $proposal, band: $band) {
              totalObservations
              totalPulsars
              edges {
                node {
                  jname
                  last
                  first
                  proposalShort
                  timespan
                  nobs
                }
              }
            }
          }`
    },
    graphql`
      query SearchTableRefetchQuery($mode: String!, $proposal: String, $band: String) {
        ...SearchTable_data @arguments(mode: $mode, proposal: $proposal, band: $band)
      }
   `
);
