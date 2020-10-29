import React, { useState, useEffect } from 'react';
import { createRefetchContainer, graphql } from 'react-relay';
import { Row, Col } from 'react-bootstrap';
import ListControls from '../components/ListControls';
import BootstrapTable from 'react-bootstrap-table-next';
import paginationFactory from 'react-bootstrap-table2-paginator';
import ToolkitProvider, { ColumnToggle } from 'react-bootstrap-table2-toolkit';

const FoldTable = ({data, relay}) => {
    const [proposal, setProposal] = useState('All');
    const [band, setBand] = useState('All');

    useEffect(() => {
        relay.refetch({mode: 'observations', proposal: proposal, band: band});
    }, [proposal, band, relay]);

    const rows = data.foldObservations.edges.reduce((result, edge) => [...result, {...edge.node}], []);
    
    const columns = [
        {dataField: 'jname', text: 'jname', sort:true},
        {dataField: 'last', text: 'Last obs', sort: true},
        {dataField: 'first', text: 'First obs', sort: true},
        {dataField: 'proposalShort', text: 'Project', sort: true},
        {dataField: 'timespan', text: 'Timespan [days]', align: 'right', headerAlign: 'right', sort: true},
        {dataField: 'nobs', text: 'Number of obs', align: 'right', headerAlign: 'right', sort: true},
        {dataField: 'totalTintH', text: 'Total int. [h]', align: 'right', headerAlign: 'right', sort: true},
        {dataField: 'avgSnr5min', text: 'Avg S/N pipe (5 mins)', align: 'right', headerAlign: 'right', sort: true},
        {dataField: 'maxSnr5min', text: 'Max S/N pipe (5 mins)', align: 'right', headerAlign: 'right', sort: true},
        {dataField: 'latestSnr', text: 'Last S/N raw', align: 'right', headerAlign: 'right', sort: true},
        {dataField: 'latestTintM', text: 'Last int. [m]', align: 'right', headerAlign: 'right', sort: true}
    ];

    const options = {
        sizePerPage: 50,
        firstPageText: 'First',
        prePageText: 'Back',
        nextPageText: 'Next',
        lastPageText: 'Last',
        showTotal: true,
        disablePageTitle: true,
    };

    const { ToggleList } = ColumnToggle;

    return (
        <ToolkitProvider
            bootstrap4 
            keyField='jname' 
            columns={columns} 
            data={rows} 
            columnToggle
            search
        >
            {props => 
                <React.Fragment>
                    <Row>
                        <Col md={4}>
                            <ListControls 
                                searchProps={props.searchProps} 
                                handleProposalFilter={setProposal} 
                                handleBandFilter={setBand}/>
                        </Col>
                        <Col md={1}>
                            <p>Observations</p>
                            <h4>{ data.foldObservations.totalObservations }</h4>
                        </Col>
                        <Col md={1}>
                            <p>Pulsars</p>
                            <h4>{ data.foldObservations.totalPulsars }</h4>
                        </Col>
                        <Col md={1}>
                            <p>Total Hours</p>
                            <h4>{ data.foldObservations.totalObservationTime }</h4>
                        </Col>
                    </Row>
                    <ToggleList className="mb-3" {...props.columnToggleProps} />
                    <BootstrapTable {...props.baseProps} pagination={paginationFactory(options)} />
                </React.Fragment>
            }
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
