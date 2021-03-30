import { Button, Col, Row } from 'react-bootstrap';
import React, { useState } from 'react';
import { columnsSizeFilter, meerWatchLink } from '../helpers';

import DataView from './DataView';
import Ephemeris from './Ephemeris';
import FoldDetailCard from './FoldDetailCard';
import Link from 'found/Link';
import { useScreenSize } from '../context/screenSize-context';

const FoldDetailTable = ({ data: { relayObservationDetails } }) => {
    const { screenSize } = useScreenSize();
    const allRows = relayObservationDetails.edges.reduce(
        (result, edge) => [
            ...result, 
            { 
                key: `${edge.node.utc}:${edge.node.beam}`,
                jname: relayObservationDetails.jname,
                ...edge.node, 
                length: `${edge.node.length} [m]`,
                action: <Link 
                    to={`/${relayObservationDetails.jname}/${edge.node.utc}/${edge.node.beam}/`}
                    size="sm" 
                    variant="outline-secondary" as={Button}>View</Link> 
            }
        ], []
    );

    const [rows, setRows] = useState(allRows);
    const [ephemerisVisable, setEphemerisVisable] = useState(false);

    const columns = [
        { dataField: 'key', text: '', sort: false, hidden: true, toggle: false },
        { dataField: 'utc', text: 'Timestamp', sort: true, headerClasses: 'fold-detail-utc' },
        { dataField: 'proposalShort', text: 'Project', sort: true, 
            screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'] },
        { dataField: 'length', text: 'Length', sort: true, screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'] },
        { dataField: 'beam', text: 'Beam', sort: true, screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'] },
        { dataField: 'bw', text: 'BW', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'nchan', text: 'Nchan', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'band', text: 'Band', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'nbin', text: 'Nbin', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'nant', text: 'Nant', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'nantEff', text: 'Nant eff', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'dmFold', text: 'DM fold', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'dmPipe', text: 'DM meerpipe', sort: true, screenSizes: ['xxl'] },
        { dataField: 'rmPipe', text: 'RM meerpipe', sort: true, screenSizes: ['xxl'] },
        { dataField: 'snrSpip', text: 'S/N backend', sort: true, screenSizes: ['xxl'] },
        { dataField: 'snrPipe', text: 'S/N meerpipe', sort: true, screenSizes: ['xxl'] },
        { dataField: 'action', text: '', sort: false, align: 'right', headerAlign: 'right' },
    ];

    const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

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
        <div className="fold-detail-table">
            <Row>
                <Col>
                    <Button 
                        size="sm"
                        variant="outline-secondary" 
                        className="mr-2 mb-2"
                        disabled={relayObservationDetails.ephemeris ? false : true}
                        onClick={() => setEphemerisVisable(true)}>
                        { relayObservationDetails.ephemeris ? 
                            'View folding ephemeris' : 'Folding ephemeris unavailable'}
                    </Button>
                    <Button 
                        size="sm mb-2"
                        as="a"
                        href={meerWatchLink(relayObservationDetails.jname)}
                        variant="outline-secondary"> 
                        View MeerWatch
                    </Button>
                </Col>
            </Row>
            {relayObservationDetails.ephemeris && <Ephemeris 
                ephemeris={relayObservationDetails.ephemeris} 
                updated={relayObservationDetails.ephemerisUpdatedAt}
                show={ephemerisVisable} 
                setShow={setEphemerisVisable} />}
            <DataView 
                summaryData={summaryData}
                columns={columnsSizeFiltered}
                rows={rows}
                setProposal={handleProjectFilter}
                setBand={handleBandFilter}
                plot
                keyField="key"
                card={FoldDetailCard}
            />
        </div>
    );
};

export default FoldDetailTable;
