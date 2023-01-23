import { Button, ButtonGroup, Col, Row } from 'react-bootstrap';
import React, { useState } from 'react';
import { columnsSizeFilter, formatDDMonYYYY, formatUTC, meerWatchLink } from '../helpers';
import DataView from './DataView';
import Ephemeris from './Ephemeris';
import FoldDetailCard from './FoldDetailCard';
import Link from 'found/Link';
import ReactMarkdown from 'react-markdown';
import { useScreenSize } from '../context/screenSize-context';

/* eslint-disable complexity */
const FoldDetailTable = ({ data: { foldObservationDetails }, jname, mainProject }) => {
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
                action: !edge.node.restricted ? <ButtonGroup vertical>
                    <Link 
                        to={`${process.env.REACT_APP_BASE_URL}/${jname}/${formatUTC(edge.node.utc)}/${edge.node.beam}/`}
                        size="sm" 
                        variant="outline-secondary" as={Button}>View</Link> 
                    <Link 
                        to={`${process.env.REACT_APP_BASE_URL}/session/${formatUTC(edge.node.utc)}/`}
                        size="sm" 
                        variant="outline-secondary" as={Button}>View session</Link> 
                </ButtonGroup> :
                    <Button
                        size="sm"
                        variant="outline-dark">
                        <span className='small'>Embargoed<br/>until<br/>{formatDDMonYYYY(edge.node.embargoEndDate) }
                        </span>
                    </Button>

            }
        ], []
    );

    const [rows, setRows] = useState(allRows);
    const [ephemerisVisible, setEphemerisVisible] = useState(false);

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

    const downloadEphemeris = async () => {
        const link = document.createElement('a');
        link.href = `${process.env.REACT_APP_MEDIA_URL}${foldObservationDetails.ephemerisLink}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };


    const downloadToas = async () => {
        const link = document.createElement('a');
        link.href = `${process.env.REACT_APP_MEDIA_URL}${foldObservationDetails.toasLink}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="fold-detail-table">
            <Row className="mb-3">
                <Col md={5}>
                    <ReactMarkdown>{foldObservationDetails.description}</ReactMarkdown>
                </Col>
            </Row>
            <Row>
                <Col>
                    <Button 
                        size="sm"
                        variant="outline-secondary" 
                        className="mr-2 mb-2"
                        disabled={ephemeris ? false : true}
                        onClick={() => setEphemerisVisible(true)}>
                        { ephemeris ? 
                            'View folding ephemeris' : 'Folding ephemeris unavailable'}
                    </Button>
                    { mainProject !== 'MONSPSR' && <Button
                        size="sm"
                        className="mr-2 mb-2"
                        as="a"
                        href={meerWatchLink(jname)}
                        variant="outline-secondary">
                        View MeerWatch
                    </Button> }
                    { localStorage.isStaff === 'true' && foldObservationDetails.ephemerisLink &&
                        <Button
                            size="sm"
                            className="mr-2 mb-2"
                            variant="outline-secondary"
                            onClick={() => downloadEphemeris()}
                        >
                            Download ephemeris
                        </Button>
                    }
                    { localStorage.isStaff === 'true' && foldObservationDetails.toasLink &&
                        <Button
                            size="sm"
                            className="mr-2 mb-2"
                            variant="outline-secondary"
                            onClick={() => downloadToas()}
                        >
                            Download TOAs
                        </Button>
                    }
                </Col>
            </Row>
            { ephemeris && <Ephemeris 
                ephemeris={ephemeris} 
                updated={ephemerisUpdated}
                show={ephemerisVisible}
                setShow={setEphemerisVisible} />}
            <DataView 
                summaryData={summaryData}
                columns={columnsSizeFiltered}
                rows={rows}
                setProject={handleProjectFilter}
                setBand={handleBandFilter}
                plot
                maxPlotLength={foldObservationDetails.maxPlotLength}
                minPlotLength={foldObservationDetails.minPlotLength}
                mainProject={mainProject}
                keyField="key"
                card={FoldDetailCard}
            />
        </div>
    );
};

export default FoldDetailTable;
