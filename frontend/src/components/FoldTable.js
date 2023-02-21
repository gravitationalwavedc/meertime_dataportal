import { Button, ButtonGroup } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { columnsSizeFilter, formatUTC } from '../helpers';
import { createRefetchContainer, graphql } from 'react-relay';
import DataView from './DataView';
import Link from 'found/Link';
import { useScreenSize } from '../context/screenSize-context';

const FoldTable = ({ data: { foldObservations: relayData }, relay, match: { location: { query } } }) => {
    const { screenSize } = useScreenSize();
    const [mainProject, setMainProject] = useState(query.mainProject || 'meertime');
    const [project, setProject] = useState(query.project || 'All');
    const [band, setBand] = useState(query.band || 'All');

    useEffect(() => {
        relay.refetch({ mainProject: mainProject, project: project, band: band });
        const url = new URL(window.location);
        url.searchParams.set('mainProject', mainProject);
        url.searchParams.set('project', project);
        url.searchParams.set('band', band);
        window.history.pushState({}, '', url);
    }, [band, project, mainProject, query, relay]);

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
        { dataField: 'allProjects', text: 'All Projects', sort: true, screenSizes: ['xxl'] },
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
            dataField: 'highestSnRaw', text: 'High S/N raw', align: 'right', headerAlign: 'right',
            sort: true, screenSizes: ['lg', 'xl', 'xxl']
        },
        {
            dataField: 'lowestSnRaw', text: 'Low S/N raw', align: 'right', headerAlign: 'right',
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
        { title: 'Unique Pulsars', value: relayData.totalPulsars },
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
            band={band}
            setBand={setBand}
            query={query}
            mainProjectSelect
            rememberSearch={true}
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
                    allProjects
                    project
                    timespan
                    numberOfObservations
                    lastSnRaw
                    highestSnRaw
                    lowestSnRaw
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
