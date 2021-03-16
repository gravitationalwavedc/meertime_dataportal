import { Button, Row } from 'react-bootstrap';
import React, { useState } from 'react';

import DataView from './DataView';
import Ephemeris from './Ephemeris';
import Link from 'found/Link';
import { meerWatchLink } from '../helpers';

const FoldDetailTable = ({ data: { relayObservationDetails } }) => {
    const allRows = relayObservationDetails.edges.reduce(
        (result, edge) => [
            ...result, 
            { 
                key: `${edge.node.utc}:${edge.node.beam}`,
                ...edge.node, 
                action: <Link 
                    to={`/${relayObservationDetails.jname}/${edge.node.utc}/${edge.node.beam}/`}
                    size="sm" 
                    variant="outline-secondary" as={Button}>View</Link> 
            }
        ], []
    );

    const [rows, setRows] = useState(allRows);
    const [ephemerisVisable, setEphemerisVisable] = useState(false);

    const fit10 = { width: '10%', whiteSpace: 'nowrap' };
    
    const columns = [
        { dataField: 'key', text: '', sort: false, hidden: true },
        { dataField: 'utc', text: 'Timestamp', sort: true, headerStyle: fit10 },
        { dataField: 'proposalShort', text: 'Project', sort: true },
        { dataField: 'length', text: 'Length [m]', sort: true },
        { dataField: 'beam', text: 'Beam', sort: true },
        { dataField: 'bw', text: 'BW', sort: true },
        { dataField: 'nchan', text: 'Nchan', sort: true },
        { dataField: 'band', text: 'Band', sort: true },
        { dataField: 'nbin', text: 'Nbin', sort: true },
        { dataField: 'nant', text: 'Nant', sort: true },
        { dataField: 'nantEff', text: 'Nant eff', sort: true },
        { dataField: 'dmFold', text: 'DM fold', sort: true },
        { dataField: 'dmPipe', text: 'DM meerpipe', sort: true },
        { dataField: 'rmPipe', text: 'RM meerpipe', sort: true },
        { dataField: 'snrSpip', text: 'S/N backend', sort: true },
        { dataField: 'snrPipe', text: 'S/N meerpipe', sort: true },
        { dataField: 'action', text: '', sort: false, align: 'center', headerAlign: 'center' },
    ];

    // totalEstimatedDiskSpace is a human readable formatted byte string in the form of "900.2\u00a0MB".
    // We split on this character so we can use the number and the units separately.
    const [size, sizeFormat] = relayObservationDetails.totalEstimatedDiskSpace.split('\u00a0');

    const handleBandFilter = (band) => {
        if(band === 'All') {
            setRows(allRows);
            return;
        }

        const newRows = allRows.filter((row) => row.band === band);
        setRows(newRows);
    };

    const handleProjectFilter = (project) => {
        if(project === 'All') {
            setRows(allRows);
            return;
        }

        const newRows = allRows.filter((row) => row.proposalShort === project);
        setRows(newRows);

    };

    const summaryData = [
        { title: 'Observations', value: relayObservationDetails.totalObservations }, 
        { title: 'Projects', value: relayObservationDetails.totalProjects }, 
        { title: 'Timespan [days]', value: relayObservationDetails.totalTimespanDays }, 
        { title: 'Hours', value: relayObservationDetails.totalObservationHours }, 
        { title: `Size [${sizeFormat}]`, value: size }, 
    ];

    return (
        <React.Fragment>
            <Row style={{ margin: '-12.5rem 0 10.5rem 0' }}>
                <Button 
                    size="sm"
                    variant="outline-secondary" 
                    className="mr-2"
                    disabled={relayObservationDetails.ephemeris ? false : true}
                    onClick={() => setEphemerisVisable(true)}>
                    { relayObservationDetails.ephemeris ? 
                        'View folding ephemeris' : 'Folding ephemeris unavailable'}
                </Button>
                <Button 
                    size="sm"
                    as="a"
                    href={meerWatchLink(relayObservationDetails.jname)}
                    variant="outline-secondary"> 
                        View MeerWatch
                </Button>
            </Row>
            {relayObservationDetails.ephemeris && <Ephemeris 
                ephemeris={relayObservationDetails.ephemeris} 
                updated={relayObservationDetails.ephemerisUpdatedAt}
                show={ephemerisVisable} 
                setShow={setEphemerisVisable} />}
            <DataView 
                summaryData={summaryData}
                columns={columns}
                rows={rows}
                setProposal={handleProjectFilter}
                setBand={handleBandFilter}
                plot
                keyField="key"
            />
        </React.Fragment>
    );
};

export default FoldDetailTable;
