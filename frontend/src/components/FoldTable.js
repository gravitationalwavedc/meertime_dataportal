import { Button, ButtonGroup } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { columnsSizeFilter, formatUTC } from '../helpers';
import { createRefetchContainer, graphql } from 'react-relay';

import DataView from './DataView';
import Link from 'found/Link';
import { useScreenSize } from '../context/screenSize-context';

const FoldTable = ({ data: { foldObservations: relayData }, relay }) => {
    const { screenSize } = useScreenSize();
    const [mainProject, setMainProject] = useState('meertime');
    const [project, setProject] = useState('All');
    const [band, setBand] = useState('All');

    useEffect(() => {
        relay.refetch({ mainProject: mainProject, project: project, band: band });
    }, [band, relay, project, mainProject]);

    const rows = relayData.edges.reduce((result, edge) => {
        const row = { ...edge.node };
        row.projectKey = mainProject;
        row.latestObservation = formatUTC(row.latestObservation);
        row.firstObservation = formatUTC(row.firstObservation);
        row.action = <ButtonGroup vertical>
            <Link
                to={`${process.env.REACT_APP_BASE_URL}/fold/${mainProject}/${row.jname}/`}
                size='sm'
                variant="outline-secondary" as={Button}>
                View all
            </Link>
            <Link
                to={`${process.env.REACT_APP_BASE_URL}/${row.jname}/${row.latestObservation}/${row.beam}/`}
                size='sm'
                variant="outline-secondary"
                as={Button}>
                View last
            </Link>
        </ButtonGroup>;
        return [...result, { ...row }];
    }, []);

    const columns = [
        { dataField: 'projectKey', hidden: true, toggle: false, sort: false, csvExport: false },
        { dataField: 'jname', text: 'JName', sort: true },
        { dataField: 'project', text: 'Project', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'latestObservation', text: 'Last', sort: true },
        { dataField: 'firstObservation', text: 'First', sort: true, screenSizes: ['xxl'] },
        {
            dataField: 'timespan', text: 'Timespan', align: 'right', headerAlign: 'right', sort: true,
            screenSizes: ['md', 'lg', 'xl', 'xxl'], formatter: cell => `${cell} [d]`
        },
        {
            dataField: 'numberOfObservations', text: 'Observations', align: 'right', headerAlign: 'right',
            sort: true, screenSizes: ['md', 'lg', 'xl', 'xxl']
        },
        {
            dataField: 'totalIntegrationHours', text: 'Total int', align: 'right', headerAlign: 'right',
            sort: true, screenSizes: ['lg', 'xl', 'xxl'], formatter: cell => `${cell} [h]`
        },
        {
            dataField: 'lastSnRaw', text: 'Last S/N raw', align: 'right', headerAlign: 'right',
            sort: true, screenSizes: ['lg', 'xl', 'xxl']
        },
        {
            dataField: 'lastIntegrationMinutes', text: 'Last int.', align: 'right', headerAlign: 'right',
            sort: true, screenSizes: ['lg', 'xl', 'xxl'], formatter: cell => `${cell} [m]`
        },
        {
            dataField: 'action', text: '', align: 'right', headerAlign: 'right', csvExport: false,
            sort: false
        }
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
            mainProject={mainProject}
            setMainProject={setMainProject}
            setBand={setBand}
        />
    );
};

export default createRefetchContainer(
    FoldTable,
    {
        data: graphql`
          fragment FoldTable_data on Query @argumentDefinitions(
            mainProject: {type: "String", defaultValue: "MEERTIME"}
            project: {type: "String", defaultValue: "All"}
            band: {type: "String", defaultValue: "All"}
          ) {
              foldObservations(
                mainProject: $mainProject,
                project: $project, 
                band: $band, 
              ) {
                totalObservations
                totalPulsars
                totalObservationTime
                edges {
                  node {
                    jname
                    beam
                    latestObservation
                    firstObservation
                    project
                    timespan
                    numberOfObservations
                    lastSnRaw
                    lastIntegrationMinutes
                    maxSnPipe
                    avgSnPipe
                    totalIntegrationHours
                  }
                }
              }
          }`
    },
    graphql`
      query FoldTableRefetchQuery($mainProject: String, $project: String, $band: String) {
        ...FoldTable_data @arguments(mainProject: $mainProject, project: $project, band: $band)
      }
   `
);

// missing
// lastBeam
