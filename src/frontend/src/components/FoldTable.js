import { Button, ButtonGroup } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { createRefetchContainer, graphql } from 'react-relay';
import { formatUTC, nullCellFormatter } from '../helpers';

import DataView from './DataView';
import Link from 'found/Link';

const FoldTable = ({ data: { relayObservations: relayData }, relay }) => {
    const [project, setProject] = useState('meertime');
    const [proposal, setProposal] = useState('All');
    const [band, setBand] = useState('All');

    useEffect(() => {
        relay.refetch({ mode: 'observations', proposal: proposal, band: band, getProposalFilters: project });
    }, [proposal, band, relay, project]);

    const rows = relayData.edges.reduce((result, edge) => { 
        const row = { ...edge.node };
        row.projectKey = project;
        row.last = formatUTC(row.last);
        row.first = formatUTC(row.first);
        row.totalTintH = `${row.totalTintH} hours`;
        row.latestTintM = `${row.latestTintM} minutes`;
        row.action = <ButtonGroup vertical>
            <Link 
                to={`/fold/${project}/${row.jname}/`} 
                size='sm' 
                variant="outline-secondary" as={Button}>
                  View all
            </Link>
            <Link 
                to={`/${row.jname}/${row.last}/${row.lastBeam}/`} 
                size='sm' 
                variant="outline-secondary" 
                as={Button}>
                  View last
            </Link>
        </ButtonGroup>;
        return [...result, { ...row }];
    }, []);

    const fit2 = { width: '2%', whiteSpace: 'nowrap' };
    const fit6 = { width: '6%', whiteSpace: 'nowrap' };
    const fit8 = { width: '8%', whiteSpace: 'nowrap' };
    
    const columns = [
        { dataField: 'jname', text: 'JName', sort:true, style: fit6, headerStyle: fit6 },
        { dataField: 'projectKey', hidden: true, sort:false },
        { dataField: 'last', text: 'Last', sort: true },
        { dataField: 'first', text: 'First', sort: true },
        { dataField: 'proposalShort', text: 'Project', sort: true, style: fit2, headerStyle: fit2 },
        { dataField: 'timespan', text: 'Timespan', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'nobs', text: 'Observations', align: 'right', headerAlign: 'right', 
            sort: true, headerStyle: fit8, style: fit8 },
        { dataField: 'totalTintH', text: 'Total int [h]', align: 'right', headerAlign: 'right', 
            sort: true, headerStyle: fit8, style: fit8 },
        { dataField: 'avgSnr5min', formatter: nullCellFormatter, text: 'Avg S/N pipe (5 mins)', align: 'right', 
            headerAlign: 'right', sort: true },
        { dataField: 'maxSnr5min', formatter: nullCellFormatter, text: 'Max S/N pipe (5 mins)', align: 'right', 
            headerAlign: 'right', sort: true },
        { dataField: 'latestSnr', text: 'Last S/N raw', align: 'right', headerAlign: 'right', 
            sort: true, headerStyle: fit8, style: fit8 },
        { dataField: 'latestTintM', text: 'Last int. [m]', align: 'right', headerAlign: 'right', 
            sort: true, headerStyle: fit8, style: fit8 },
        { dataField: 'action', text: '', align: 'center', headerAlign: 'center', 
            sort: false, headerStyle: fit8, style: fit8 }
    ];

    const summaryData = [
        { title: 'Observations', value: relayData.totalObservations },
        { title: 'Pulsars', value: relayData.totalPulsars },
        { title: 'Hours', value: relayData.totalObservationTime },
    ];

    return (
        <DataView
            summaryData={summaryData}
            columns={columns}
            rows={rows}
            setProject={setProject}
            project={project}
            setProposal={setProposal}
            setBand={setBand}
        />
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
            getProposalFilters: {type: "String", defaultValue: "meertime"}
          ) {
              relayObservations(
                mode: $mode, 
                proposal: $proposal, 
                band: $band, 
                getProposalFilters: $getProposalFilters
              ) {
                totalObservations
                totalPulsars
                totalObservationTime
                edges {
                  node {
                    jname
                    last
                    lastBeam
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
      query FoldTableRefetchQuery($mode: String!, $proposal: String, $band: String, $getProposalFilters: String) {
  ...FoldTable_data @arguments(mode: $mode, proposal: $proposal, band: $band, getProposalFilters:$getProposalFilters)
      }
   `
);
