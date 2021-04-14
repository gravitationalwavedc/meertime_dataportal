import React, { useState } from 'react';
import { columnsSizeFilter, kronosLink } from '../helpers';

import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import DataView from './DataView';
import Ephemeris from './Ephemeris';
import Row from 'react-bootstrap/Row';
import SearchmodeDetailCard from './SearchmodeDetailCard';
import { useScreenSize } from '../context/screenSize-context';

const SearchmodeDetailTable = ({ data }) => {
    const { screenSize } = useScreenSize();
    const allRows = data.relaySearchmodeDetails.edges.reduce(
        (result, edge) => [...result, 
            { 
                key: `${edge.node.utc}:${edge.node.beam}`,
                ...edge.node, 
                jname: data.relaySearchmodeDetails.jname,
                action: <Button
                    href={kronosLink(edge.node.beam, data.relaySearchmodeDetails.jname, edge.node.utc)} 
                    as="a"
                    size='sm' 
                    variant="outline-secondary" 
                >View</Button> }],
        []);

    const [rows, setRows] = useState(allRows);
    const [ephemerisVisable, setEphemerisVisable] = useState(false);

    const columns = [
        { dataField: 'key', text: '', sort: false, hidden: true, toggle: false },
        { dataField: 'utc', text: 'Timestamp', sort: true, headerClasses: 'fold-detail-utc' },
        { dataField: 'proposalShort', text: 'Project', sort: true, screenSizes: ['md', 'lg', 'xl', 'xxl'] },
        { dataField: 'ra', text: 'RA', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'dec', text: 'DEC', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'length', text: 'Length [m]', sort: true, screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'] },
        { dataField: 'beam', text: 'Beam', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'frequency', text: 'Frequency [MHz]', sort: true, screenSizes: ['xxl'] },
        { dataField: 'nchan', text: 'Nchan', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'nbit', text: 'Nbit', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'nantEff', text: 'Nant Eff', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'npol', text: 'Npol', sort: true, screenSizes: ['xxl'] },
        { dataField: 'dm', text: 'DM', sort: true, screenSizes: ['xxl'] },
        { dataField: 'tsamp', text: 'tSamp [μs]', sort: true, screenSizes: ['xxl'] },
        { dataField: 'action', text: '', align: 'right', headerAlign: 'right', sort: false }
    ];

    const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

    const handleProjectFilter = (project) => {
        if(project === 'All') {
            setRows(allRows);
            return;
        }

        const newRows = allRows.filter((row) => row.proposalShort === project);
        setRows(newRows);

    };

    const summaryData = [
        { title: 'Observations', value: data.relaySearchmodeDetails.totalObservations },
        { title: 'Projects', value: data.relaySearchmodeDetails.totalProjects },
        { title: 'Timespan', value: data.relaySearchmodeDetails.totalTimespanDays }
    ];

    return <div className="search-detail">
        <Row>
            <Col className="emphemeris-col">
                <Button 
                    size="sm"
                    variant="outline-secondary" 
                    className="mr-2"
                    disabled={data.relaySearchmodeDetails.ephemeris ? false : true}
                    onClick={() => setEphemerisVisable(true)}>
                    { data.relaySearchmodeDetails.ephemeris ? 
                        'View folding ephemeris' : 'Folding ephemeris unavailable'}
                </Button>
            </Col>
        </Row>
        {data.relaySearchmodeDetails.ephemeris && <Ephemeris 
            ephemeris={data.relaySearchmodeDetails.ephemeris} 
            updated={data.relaySearchmodeDetails.ephemerisUpdatedAt}
            show={ephemerisVisable} 
            setShow={setEphemerisVisable} />}
        <DataView 
            summaryData={summaryData}
            columns={columnsSizeFiltered}
            rows={rows}
            setProposal={handleProjectFilter}
            keyField='key'
            card={SearchmodeDetailCard}
        />
    </div>;
};

export default SearchmodeDetailTable;
