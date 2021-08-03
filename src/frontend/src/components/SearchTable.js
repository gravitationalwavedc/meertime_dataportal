import { Button, ButtonGroup } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { columnsSizeFilter, formatUTC, kronosLink } from '../helpers';
import { createRefetchContainer, graphql } from 'react-relay';

import DataView from './DataView';
import Link from 'found/Link';
import SearchmodeCard from './SearchmodeCard';
import { useScreenSize } from '../context/screenSize-context';

const SearchTable = ({ data: { relayObservations }, relay }) => {
    const { screenSize } = useScreenSize();
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
        row.projectKey = project;
        row.action = <ButtonGroup vertical>
            <Link 
                to={`${process.env.REACT_APP_BASE_URL}/search/${project}/${row.jname}/`} 
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

    const columns = [
        { dataField: 'jname', text: 'JName', sort:true },
        { dataField: 'proposalShort', text: 'Project', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'last', text: 'Last', sort: true },
        { dataField: 'first', text: 'First', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'timespan', text: 'Timespan', align: 'right', headerAlign: 'right', sort: true, 
            screenSizes: ['md', 'lg', 'xl', 'xxl'] },
        { dataField: 'nobs', text: 'Observations', align: 'right', headerAlign: 'right', 
            sort: true },
        { dataField: 'action', text: '', align: 'center', headerAlign: 'center', 
            sort: false }
    ];

    const columnsForScreenSize = columnsSizeFilter(columns, screenSize);

    const summaryData = [
        { title: 'Observations', value: relayObservations.totalObservations },
        { title: 'Pulsars', value: relayObservations.totalPulsars }
    ];

    return (
        <div className="searchmode-table">
            <DataView
                summaryData={summaryData}
                columns={columnsForScreenSize}
                rows={rows}
                setProposal={setProposal}
                setBand={setBand}
                setProject={setProject}
                project={project}
                card={SearchmodeCard}
            />
        </div>
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
