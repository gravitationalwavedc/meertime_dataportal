import React, { useState } from 'react';
import { columnsSizeFilter, kronosLink } from '../helpers';

import Button from 'react-bootstrap/Button';
import DataView from './DataView';
import SearchmodeDetailCard from './SearchmodeDetailCard';
import { formatUTC } from '../helpers';
import { useScreenSize } from '../context/screenSize-context';

const SearchmodeDetailTable = ({ data, jname }) => {
    const { screenSize } = useScreenSize();
    const allRows = data.searchmodeObservationDetails.edges.reduce(
        (result, edge) => [...result, 
            { 
                ...edge.node, 
                key: `${edge.node.utc}:${edge.node.beam}`,
                jname: jname,
                utc: formatUTC(edge.node.utc),
                action: <Button
                    href={kronosLink(edge.node.beam, jname, formatUTC(edge.node.utc))} 
                    as="a"
                    size='sm' 
                    variant="outline-secondary" 
                >View</Button> }],
        []);

    const [rows, setRows] = useState(allRows);

    const columns = [
        { dataField: 'key', text: '', sort: false, hidden: true, toggle: false },
        { dataField: 'utc', text: 'Timestamp', sort: true, headerClasses: 'fold-detail-utc' },
        { dataField: 'project', text: 'Project', sort: true, screenSizes: ['md', 'lg', 'xl', 'xxl'] },
        { dataField: 'ra', text: 'RA', sort: true, screenSizes: ['lg', 'xl', 'xxl'], align: 'right', 
            headerAlign: 'right' },
        { dataField: 'dec', text: 'DEC', sort: true, screenSizes: ['lg', 'xl', 'xxl'], align: 'right', 
            headerAlign: 'right' },
        { dataField: 'length', text: 'Length', sort: true, screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'], 
            align: 'right', headerAlign: 'right', formatter: cell => `${cell} [m]` },
        { dataField: 'beam', text: 'Beam', sort: true, screenSizes: ['lg', 'xl', 'xxl'], align: 'right', 
            headerAlign: 'right' },
        { dataField: 'frequency', text: 'Frequency', sort: true, screenSizes: ['xxl'], align: 'right', 
            headerAlign: 'right', formatter: cell => `${cell} [Mhz]` },
        { dataField: 'nchan', text: 'Nchan', sort: true, screenSizes: ['xl', 'xxl'], align: 'right', 
            headerAlign: 'right' },
        { dataField: 'nbit', text: 'Nbit', sort: true, screenSizes: ['xl', 'xxl'], align: 'right', 
            headerAlign: 'right' },
        { dataField: 'nantEff', text: 'Nant Eff', sort: true, screenSizes: ['xl', 'xxl'], align: 'right', 
            headerAlign: 'right' },
        { dataField: 'npol', text: 'Npol', sort: true, screenSizes: ['xxl'], align: 'right', 
            headerAlign: 'right' },
        { dataField: 'dm', text: 'DM', sort: true, screenSizes: ['xxl'], align: 'right', headerAlign: 'right' },
        { dataField: 'tsamp', text: 'tSamp', sort: true, screenSizes: ['xxl'], align: 'right', 
            headerAlign: 'right', formatter: cell => `${cell} [μs]` },
        { dataField: 'action', text: '', align: 'right', headerAlign: 'right', sort: false }
    ];

    const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

    const handleProjectFilter = (project) => {
        if(project === 'All') {
            setRows(allRows);
            return;
        }

        const newRows = allRows.filter((row) => row.project === project);
        setRows(newRows);

    };

    const summaryData = [
        { title: 'Observations', value: data.searchmodeObservationDetails.totalObservations },
        { title: 'Projects', value: data.searchmodeObservationDetails.totalProjects },
        { title: 'Timespan', value: data.searchmodeObservationDetails.totalTimespanDays }
    ];

    return <div className="search-detail">
        <DataView 
            summaryData={summaryData}
            columns={columnsSizeFiltered}
            rows={rows}
            setProject={handleProjectFilter}
            keyField='key'
            card={SearchmodeDetailCard}
        />
    </div>;
};

export default SearchmodeDetailTable;
