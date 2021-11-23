import { Button, ButtonGroup } from 'react-bootstrap';
import React, { useState } from 'react';
import { createRefetchContainer, graphql } from 'react-relay';
import DataView from './DataView';
import Link from 'found/Link';
import { formatUTC } from '../helpers';

const SessionListTable = ({ data: { sessionList } }) => {
    const allRows = sessionList.edges.reduce((result, edge) => {
        const row = { ...edge.node };
        row.start = formatUTC(row.start);
        row.end = formatUTC(row.end);
        row.key = `${row.start}-${row.end}`;
        row.action = <ButtonGroup vertical>
            <Link 
                to={`${process.env.REACT_APP_BASE_URL}/session/${row.start}/${row.end}/`} 
                size='sm' 
                variant="outline-secondary" as={Button}>
                  View all
            </Link>
        </ButtonGroup>;
        return [ ...result, { ...row }];
    }, []); 

    const [rows, setRows] = useState(allRows);

    const columns = [
        { dataField: 'key', sort: false, hidden: true, toggle: false, csvExport: false },
        { dataField: 'start', text: 'Start' },
        { dataField: 'end', text: 'End' },
        { dataField: 'projects', text: 'Projects' },
        { dataField: 'numberOfObservations', text: 'Observations', align: 'right', headerAlign: 'right' },
        { dataField: 'frequency', text: 'Frequency', align: 'right', headerAlign: 'right' },
        { dataField: 'totalIntegration', text: 'Total Int', formatter: cell => `${cell} [s]`, align: 'right', 
            headerAlign: 'right' },
        { dataField: 'nDishMin', text: 'NDISH (min)', align: 'right', headerAlign: 'right' },
        { dataField: 'nDishMax', text: 'NDISH (max)', align: 'right', headerAlign: 'right' },
        { dataField: 'zapFraction', text: 'Zap fraction (%)', align: 'right', headerAlign: 'right' },
        { dataField: 'listOfPulsars', hidden: true },
        { dataField: 'action', text: '', align: 'right', headerAlign: 'right', sort: false }
    ];

    const summaryData = [
        { title: 'Sessions', value: rows.length }
    ];

    const handleProjectFilter = (project) => {
        if(project === 'All') {
            setRows(allRows);
            return;
        }
        const newRows = allRows.filter((row) => row.projects.toLowerCase().includes(project.toLowerCase()));
        setRows(newRows);

    };

    return <DataView 
        summaryData={summaryData} 
        columns={columns} 
        rows={rows}
        setProject={handleProjectFilter}
        keyField="key"/>;
};

export default createRefetchContainer(
    SessionListTable,
    {
        data: graphql`
            fragment SessionListTable_data on Query {
                sessionList {
                    edges {
                        node {
                            start
                            end
                            numberOfObservations
                            numberOfPulsars
                            listOfPulsars
                            frequency
                            projects
                            totalIntegration
                            nDishMin
                            nDishMax
                            zapFraction
                        }
                    }
                }
            }`
    },
    graphql`
        query SessionListTableRefetchQuery {
            ...SessionListTable_data
        }
    `
);
