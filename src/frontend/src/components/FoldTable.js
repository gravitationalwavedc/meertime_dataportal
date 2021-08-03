import { Button, ButtonGroup } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { columnsSizeFilter, formatUTC, nullCellFormatter } from '../helpers';
import { createRefetchContainer, graphql } from 'react-relay';

import DataView from './DataView';
import Link from 'found/Link';
import { useScreenSize } from '../context/screenSize-context';

const FoldTable = ({ data: { relayObservations: relayData }, relay }) => {
    const { screenSize } = useScreenSize();
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
        row.totalTintH = `${row.totalTintH} [h]`;
        row.latestTintM = `${row.latestTintM} [m]`;
        row.action = <ButtonGroup vertical>
            <Link 
                to={`${process.env.REACT_APP_BASE_URL}/fold/${project}/${row.jname}/`} 
                size='sm' 
                variant="outline-secondary" as={Button}>
                  View all
            </Link>
            <Link 
                to={`${process.env.REACT_APP_BASE_URL}/${row.jname}/${row.last}/${row.lastBeam}/`} 
                size='sm' 
                variant="outline-secondary" 
                as={Button}>
                  View last
            </Link>
        </ButtonGroup>;
        return [...result, { ...row }];
    }, []);

    const columns = [
        { dataField: 'projectKey', hidden: true, toggle: false, sort:false },
        { dataField: 'jname', text: 'JName', sort:true },
        { dataField: 'proposalShort', text: 'Project', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'last', text: 'Last', sort: true },
        { dataField: 'first', text: 'First', sort: true, screenSizes: ['xxl'] },
        { dataField: 'timespan', text: 'Timespan', align: 'right', headerAlign: 'right', sort: true, 
            screenSizes: ['md', 'lg', 'xl', 'xxl'] },
        { dataField: 'nobs', text: 'Observations', align: 'right', headerAlign: 'right', 
            sort: true, screenSizes: ['md', 'lg', 'xl', 'xxl'] },
        { dataField: 'totalTintH', text: 'Total int [h]', align: 'right', headerAlign: 'right', 
            sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'avgSnr5min', formatter: nullCellFormatter, text: 'Avg S/N pipe (5 mins)', align: 'right', 
            headerAlign: 'right', sort: true, hidden: true },
        { dataField: 'maxSnr5min', formatter: nullCellFormatter, text: 'Max S/N pipe (5 mins)', align: 'right', 
            headerAlign: 'right', sort: true, hidden: true },
        { dataField: 'latestSnr', text: 'Last S/N raw', align: 'right', headerAlign: 'right', 
            sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'latestTintM', text: 'Last int. [m]', align: 'right', headerAlign: 'right', 
            sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'action', text: '', align: 'right', headerAlign: 'right', 
            sort: false }
    ];

    const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

    const summaryData = [
        { title: 'Observations', value: relayData.totalObservations },
        { title: 'Pulsars', value: relayData.totalPulsars },
        { title: 'Hours', value: relayData.totalObservationTime },
    ];

    return (
        <DataView
            summaryData={summaryData}
            columns={columnsSizeFiltered}
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
