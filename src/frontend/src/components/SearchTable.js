import { Button, ButtonGroup } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { createRefetchContainer, graphql } from 'react-relay';
import { formatUTC, kronosLink } from '../helpers';

import DataView from './DataView';
import Link from 'found/Link';

const SearchTable = ({ data: { relayObservations }, relay }) => {
    const [project, setProject] = useState('meertime');
    const [proposal, setProposal] = useState('All');
    const [band, setBand] = useState('All');

    useEffect(() => {
        relay.refetch({ mode: 'searchmode', proposal: proposal, band: band, getProposalFilters: project });
    }, [proposal, band, relay, project]);

    const rows = relayObservations.edges.reduce((result, edge) => { 
        const row = { ...edge.node };
        row.last = formatUTC(row.last);
        row.first = formatUTC(row.first);
        row.totalTintH = `${row.totalTintH} hours`;
        row.latestTintM = `${row.latestTintM} minutes`;
        row.action = <ButtonGroup vertical>
            <Link 
                to={`/search/${project}/${row.jname}/`} 
                size='sm' 
                variant="outline-secondary" 
                as={Button}>
                  View all
            </Link>
            <Button
                href={kronosLink(row.lastBeam, row.jname, row.last)} 
                as="a"
                size='sm' 
                variant="outline-secondary">
                  View last
            </Button>
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


    const summaryData = [
        { title: 'Observations', value: relayObservations.totalObservations },
        { title: 'Pulsars', value: relayObservations.totalPulsars }
    ];

    return (
        <DataView
            summaryData={summaryData}
            columns={columns}
            rows={rows}
            setProposal={setProposal}
            setBand={setBand}
            setProject={setProject}
            project={project}/>
    );
};

export default createRefetchContainer(
    SearchTable,
    {
        data: graphql`
          fragment SearchTable_data on Query @argumentDefinitions(
            mode: {type: "String", defaultValue: "searchmode"},
            proposal: {type: "String", defaultValue: "All"},
            band: {type: "String", defaultValue: "All"},
            getProposalFilters: {type: "String", defaultValue: "meertime"}
          ) {
          relayObservations(mode: $mode, proposal: $proposal, band: $band, getProposalFilters: $getProposalFilters) {
              totalObservations
              totalPulsars
              edges {
                node {
                  jname
                  last
                  lastBeam
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
      query SearchTableRefetchQuery($mode: String!, $proposal: String, $band: String, $getProposalFilters: String) {
        ...SearchTable_data @arguments(
          mode: $mode, 
          proposal: $proposal, 
          band: $band, 
          getProposalFilters: $getProposalFilters
        )
      }
   `
);
