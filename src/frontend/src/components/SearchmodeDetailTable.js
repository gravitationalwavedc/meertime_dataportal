import React, { useState } from 'react';

import Button from 'react-bootstrap/Button';
import DataView from './DataView';
import Ephemeris from './Ephemeris';
import Row from 'react-bootstrap/Row';
import { kronosLink } from '../helpers';

const SearchmodeDetailTable = ({ data }) => {
    const allRows = data.relaySearchmodeDetails.edges.reduce(
        (result, edge) => [...result, 
            { 
                key: `${edge.node.utc}:${edge.node.beam}`,
                ...edge.node, 
                action: <Button
                    href={kronosLink(edge.node.beam, data.relaySearchmodeDetails.jname, edge.node.utc)} 
                    as="a"
                    size='sm' 
                    variant="outline-secondary" 
                >View</Button> }],
        []);

    const [rows, setRows] = useState(allRows);
    const [ephemerisVisable, setEphemerisVisable] = useState(false);

    const fit10 = { width: '10%', whiteSpace: 'nowrap' };
    
    const columns = [
        { dataField: 'key', text: '', sort: false, hidden: true },
        { dataField: 'utc', text: 'Timestamp', sort: true, headerStyle: fit10 },
        { dataField: 'proposalShort', text: 'Project', sort: true },
        { dataField: 'ra', text: 'RA', sort: true },
        { dataField: 'dec', text: 'DEC', sort: true },
        { dataField: 'length', text: 'Length [m]', sort: true },
        { dataField: 'beam', text: 'Beam', sort: true },
        { dataField: 'frequency', text: 'Frequency [MHz]', sort: true },
        { dataField: 'nchan', text: 'Nchan', sort: true },
        { dataField: 'nbit', text: 'Nbit', sort: true },
        { dataField: 'nantEff', text: 'Nant Eff', sort: true },
        { dataField: 'npol', text: 'Npol', sort: true },
        { dataField: 'dm', text: 'DM', sort: true },
        { dataField: 'tsamp', text: 'tSamp [μs]', sort: true },
        { dataField: 'action', text: '', align: 'center', headerAlign: 'center', sort: false }
    ];

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

    return <React.Fragment>
        <Row style={{ margin: '-12.5rem 0 10.5rem 0' }}>
            <Button 
                size="sm"
                variant="outline-secondary" 
                className="mr-2"
                disabled={data.relaySearchmodeDetails.ephemeris ? false : true}
                onClick={() => setEphemerisVisable(true)}>
                { data.relaySearchmodeDetails.ephemeris ? 
                    'View folding ephemeris' : 'Folding ephemeris unavailable'}
            </Button>
        </Row>
        {data.relaySearchmodeDetails.ephemeris && <Ephemeris 
            ephemeris={data.relaySearchmodeDetails.ephemeris} 
            updated={data.relaySearchmodeDetails.ephemerisUpdatedAt}
            show={ephemerisVisable} 
            setShow={setEphemerisVisable} />}
        <DataView 
            summaryData={summaryData}
            columns={columns}
            rows={rows}
            setProposal={handleProjectFilter}
            keyField='key'
        />
    </React.Fragment>;
};

export default SearchmodeDetailTable;
