import { Button, ButtonGroup } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { columnsSizeFilter, formatUTC, kronosLink } from '../helpers';
import { createRefetchContainer, graphql } from 'react-relay';

import DataView from './DataView';
import Link from 'found/Link';
import SearchmodeCard from './SearchmodeCard';
import { useScreenSize } from '../context/screenSize-context';

const SearchTable = ({ data: { searchmodeObservations }, relay }) => {
    const { screenSize } = useScreenSize();
    const [mainProject, setMainProject] = useState('meertime');
    const [project, setProject] = useState('All');
    const [band, setBand] = useState('All');

    useEffect(() => {
        relay.refetch({ mainProject: mainProject, project: project, band: band });
    }, [band, relay, mainProject, project]);

    const rows = searchmodeObservations.edges.reduce((result, edge) => { 
        const row = { ...edge.node };
        row.projectKey = mainProject;
        row.latestObservation = formatUTC(row.latetestObservation);
        row.firstObservation = formatUTC(row.firstObservation);
        row.totalIntegrationHours = `${row.totalIntegrationHours} [h]`;
        row.lastIntegrationMinutes = `${row.lastIntegrationMinutes} [m]`;
        row.action = <ButtonGroup vertical>
            <Link 
                to={`${process.env.REACT_APP_BASE_URL}/search/${mainProject}/${row.jname}/`} 
                size='sm' 
                variant="outline-secondary" 
                as={Button}>
                  View all
            </Link>
            <Button
                href={kronosLink(row.beam, row.jname, row.latestObservation)} 
                as="a"
                size='sm' 
                variant="outline-secondary">
                  View last
            </Button>
        </ButtonGroup>;
        return [...result, { ...row }]; }, []);

    const columns = [
        { dataField: 'jname', text: 'JName', sort:true },
        { dataField: 'project', text: 'Project', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'latestObservation', text: 'Last', sort: true },
        { dataField: 'firstObservation', text: 'First', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'timespan', text: 'Timespan', align: 'right', headerAlign: 'right', sort: true, 
            screenSizes: ['md', 'lg', 'xl', 'xxl'] },
        { dataField: 'numberOfObservations', text: 'Observations', align: 'right', headerAlign: 'right', 
            sort: true },
        { dataField: 'action', text: '', align: 'center', headerAlign: 'center', 
            sort: false }
    ];

    const columnsForScreenSize = columnsSizeFilter(columns, screenSize);

    const summaryData = [
        { title: 'Observations', value: searchmodeObservations.totalObservations },
        { title: 'Pulsars', value: searchmodeObservations.totalPulsars }
    ];

    return (
        <div className="searchmode-table">
            <DataView
                summaryData={summaryData}
                columns={columnsForScreenSize}
                rows={rows}
                setProject={setProject}
                project={project}
                mainProject={mainProject}
                setMainProject={setMainProject}
                setBand={setBand}
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
            mainProject: {type: "String", defaultValue: "MEERTIME"}
            project: {type: "String", defaultValue: "All"},
            band: {type: "String", defaultValue: "All"},
          ) {
              searchmodeObservations(mainProject: $mainProject, project: $project, band: $band) {
                totalObservations
                totalPulsars
              edges {
                node {
                  jname
                  latestObservation
                  firstObservation
                  project
                  timespan
                  numberOfObservations
                }
              }
            }
          }`
    },
    graphql`
      query SearchTableRefetchQuery($mainProject: String, $project: String, $band: String) {
        ...SearchTable_data @arguments(
          mainProject: $mainProject,
          project: $project, 
          band: $band, 
        )
      }
   `
);

// missing
// lastBeam
