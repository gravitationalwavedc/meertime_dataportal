import { Button, ButtonGroup, Col, Row } from 'react-bootstrap';
import React, { useState } from 'react';
import { columnsSizeFilter, meerWatchLink } from '../helpers';

import DataView from './DataView';
import Ephemeris from './Ephemeris';
import FoldDetailCard from './FoldDetailCard';
import Link from 'found/Link';
import { formatUTC } from '../helpers';
import { useScreenSize } from '../context/screenSize-context';

const FoldDetailTable = ({ data: { foldObservationDetails }, jname }) => {
    const { screenSize } = useScreenSize();
    const allRows = foldObservationDetails.edges.reduce(
        (result, edge) => [
            ...result, 
            { 
                ...edge.node, 
                key: `${edge.node.utc}:${edge.node.beam}`,
                jname: jname,
                utc: formatUTC(edge.node.utc),
                plotLink: `${process.env.REACT_APP_BASE_URL}/${jname}/${formatUTC(edge.node.utc)}/${edge.node.beam}/`,
                action: <ButtonGroup vertical>
                    <Link 
                        to={`${process.env.REACT_APP_BASE_URL}/${jname}/${formatUTC(edge.node.utc)}/${edge.node.beam}/`}
                        size="sm" 
                        variant="outline-secondary" as={Button}>View</Link> 
                    <Link 
                        to={`${process.env.REACT_APP_BASE_URL}/session/${formatUTC(edge.node.utc)}/`}
                        size="sm" 
                        variant="outline-secondary" as={Button}>View session</Link> 
                </ButtonGroup>
            }
        ], []
    );

    const [rows, setRows] = useState(allRows);
    const [ephemerisVisable, setEphemerisVisable] = useState(false);

    const ephemeris = foldObservationDetails.edges[foldObservationDetails.edges.length -1 ].node.ephemeris;
    const ephemerisUpdated = 
        foldObservationDetails.edges[foldObservationDetails.edges.length -1 ].node.ephemerisIsUpdatedAt;

    const columns = [
        { dataField: 'key', text: '', sort: false, hidden: true, toggle: false, csvExport: false },
        { dataField: 'plotLink', text: '', sort: false, hidden: true, toggle: false, csvExport: false },
        { dataField: 'utc', text: 'Timestamp', sort: true, headerClasses: 'fold-detail-utc' },
        { dataField: 'project', text: 'Project', sort: true, 
            screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'] },
        { dataField: 'length', text: 'Length', sort: true, screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'],
            formatter: (cell) => `${cell} [m]`, align: 'right', headerAlign: 'right' },
        { dataField: 'beam', text: 'Beam', sort: true, screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'], 
            align: 'right', headerAlign: 'right' },
        { dataField: 'bw', text: 'BW', sort: true, screenSizes: ['lg', 'xl', 'xxl'], 
            align: 'right', headerAlign: 'right' },
        { dataField: 'nchan', text: 'Nchan', sort: true, screenSizes: ['lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right' },
        { dataField: 'band', text: 'Band', sort: true, screenSizes: ['lg', 'xl', 'xxl'] },
        { dataField: 'nbin', text: 'Nbin', sort: true, screenSizes: ['lg', 'xl', 'xxl'],
            align: 'right', headerAlign: 'right' },
        { dataField: 'nant', text: 'Nant', sort: true, screenSizes: ['lg', 'xl', 'xxl'], 
            align: 'right', headerAlign: 'right' },
        { dataField: 'nantEff', text: 'Nant eff', sort: true, screenSizes: ['xl', 'xxl'], 
            align: 'right', headerAlign: 'right' },
        { dataField: 'dmFold', text: 'DM fold', sort: true, screenSizes: ['xl', 'xxl'], 
            align: 'right', headerAlign: 'right' },
        { dataField: 'dmMeerpipe', text: 'DM meerpipe', sort: true, screenSizes: ['xxl'], 
            align: 'right', headerAlign: 'right' },
        { dataField: 'rmMeerpipe', text: 'RM meerpipe', sort: true, screenSizes: ['xxl'], 
            align: 'right', headerAlign: 'right' },
        { dataField: 'snBackend', text: 'S/N backend', sort: true, screenSizes: ['xxl'], 
            align: 'right', headerAlign: 'right' },
        { dataField: 'snMeerpipe', text: 'S/N meerpipe', sort: true, screenSizes: ['xxl'], 
            align: 'right', headerAlign: 'right' },
        { dataField: 'action', text: '', sort: false, align: 'right', headerAlign: 'right', csvExport: false },
    ];

    const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

    // totalEstimatedDiskSpace is a human readable formatted byte string in the form of "900.2\u00a0MB".
    // We split on this character so we can use the number and the units separately.
    const [size, sizeFormat] = foldObservationDetails.totalEstimatedDiskSpace.split('\u00a0');

    const handleBandFilter = (band) => {
        if(band.toLowerCase() === 'all') {
            setRows(allRows);
            return;
        }

        const newRows = allRows.filter((row) => row.band.toLowerCase() === band.toLowerCase());
        setRows(newRows);
    };

    const handleProjectFilter = (project) => {
        if(project === 'All') {
            setRows(allRows);
            return;
        }

        const newRows = allRows.filter((row) => row.project.toLowerCase() === project.toLowerCase());
        setRows(newRows);

    };

    const summaryData = [
        { title: 'Observations', value: foldObservationDetails.totalObservations }, 
        { title: 'Projects', value: foldObservationDetails.totalProjects }, 
        { title: 'Timespan [days]', value: foldObservationDetails.totalTimespanDays }, 
        { title: 'Hours', value: foldObservationDetails.totalObservationHours }, 
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
                        disabled={ephemeris ? false : true}
                        onClick={() => setEphemerisVisable(true)}>
                        { ephemeris ? 
                            'View folding ephemeris' : 'Folding ephemeris unavailable'}
                    </Button>
                    <Button 
                        size="sm mb-2"
                        as="a"
                        href={meerWatchLink(jname)}
                        variant="outline-secondary"> 
                        View MeerWatch
                    </Button>
                </Col>
            </Row>
            { ephemeris && <Ephemeris 
                ephemeris={ephemeris} 
                updated={ephemerisUpdated}
                show={ephemerisVisable} 
                setShow={setEphemerisVisable} />}
            <DataView 
                summaryData={summaryData}
                columns={columnsSizeFiltered}
                rows={rows}
                setProject={handleProjectFilter}
                setBand={handleBandFilter}
                plot
                maxPlotLength={foldObservationDetails.maxPlotLength}
                minPlotLength={foldObservationDetails.minPlotLength}
                keyField="key"
                card={FoldDetailCard}
            />
        </div>
    );
};

export default FoldDetailTable;
