import { Button, ButtonGroup } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { columnsSizeFilter, formatUTC } from '../helpers';
import { createRefetchContainer, graphql } from 'react-relay';

import DataView from './DataView';
import LightBox from 'react-image-lightbox';
import Link from 'found/Link';
import SessionCard from './SessionCard';
import SessionImage from './SessionImage';
import moment from 'moment';
import { useScreenSize } from '../context/screenSize-context';

const SessionTable = ({ data: { sessionDisplay }, relay, utc }) => {
    const { screenSize } = useScreenSize();
    const [project, setProject] = useState('All');
    const [isLightBoxOpen, setIsLightBoxOpen] = useState(false);
    const [lightBoxImages, setLightBoxImages] = useState({ images: [], imagesIndex: 0 });

    useEffect(() => {
        if(utc !== undefined) {
            relay.refetch({ start: null, end: null, utc: utc, project: project });
        } else {
            relay.refetch({ start: sessionDisplay.start, end: sessionDisplay.end, utc: null, project: project });
        }
    }, [project, relay, sessionDisplay.end, sessionDisplay.start, utc]);

    const startDate = moment.parseZone(sessionDisplay.start, moment.ISO_8601).format('h:mma DD/MM/YYYY');
    const endDate = moment.parseZone(sessionDisplay.end, moment.ISO_8601).format('h:mma DD/MM/YYYY');

    const openLightBox = (images, imageIndex) => {
        setIsLightBoxOpen(true);
        setLightBoxImages({ images: images, imagesIndex: imageIndex });
    };

    const rows = sessionDisplay.sessionPulsars.edges.reduce((result, edge) => { 
        const row = { ...edge.node };
        row.utc = formatUTC(row.utc);
        row.projectKey = project;
        
        const images = [
            `${process.env.REACT_APP_MEDIA_URL}${row.profileHi}`,
            `${process.env.REACT_APP_MEDIA_URL}${row.phaseVsTimeHi}`,
            `${process.env.REACT_APP_MEDIA_URL}${row.phaseVsFrequencyHi}`
        ];

        row.profile = <SessionImage 
            imageHi={row.profileHi} 
            imageLo={row.profileLo}
            images={images}
            imageIndex={0}
            openLightBox={openLightBox} />;
        row.phaseVsTime = <SessionImage
            imageHi={row.phaseVsTimeHi}
            imageLo={row.phaseVsTimeLo}
            images={images}
            imageIndex={1}
            openLightBox={openLightBox} />;
        row.phaseVsFrequency = <SessionImage
            imageHi={row.phaseVsFrequencyHi}
            imageLo={row.phaseVsFrequencyLo}
            images={images}
            imageIndex={2}
            openLightBox={openLightBox} />;
        row.action = <ButtonGroup vertical>
            <Link 
                to={`${process.env.REACT_APP_BASE_URL}/${row.pulsarType}/meertime/${row.jname}/`} 
                size='sm' 
                variant="outline-secondary" as={Button}>
                  View all
            </Link>
            <Link 
                to={`${process.env.REACT_APP_BASE_URL}/${row.jname}/${row.utc}/${row.beam}/`} 
                size='sm' 
                variant="outline-secondary" 
                as={Button}>
                  View last
            </Link>
        </ButtonGroup>;
        return [ ...result, { ...row }];
    }, []);

    const columns = [
        { dataField: 'jname', text: 'JName', sort:true },
        { dataField: 'project', text: 'Project', sort: true, screenSizes: ['md', 'lg', 'xl', 'xxl'] },
        { dataField: 'utc', text: 'UTC', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'backendSN', text: 'Backend S/N', align: 'right', headerAlign: 'right', sort: true, 
            screenSizes: ['xl', 'xxl'] },
        { dataField: 'integrations', text: 'Integration', align: 'right', headerAlign: 'right', sort: true, 
            formatter: cell => `${cell} [s]`, screenSizes: ['xl', 'xxl'] },
        { dataField: 'frequency', text: 'Frequency', align: 'right', headerAlign: 'right', sort: true, 
            formatter: cell => `${cell} Mhz`, screenSizes: ['xxl'] },
        { dataField: 'profile', text: '', align: 'center', headerAlign: 'center', sort: false },
        { dataField: 'phaseVsTime', text: '', align: 'center', headerAlign: 'center', sort: false, 
            screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'] },
        { 
            dataField: 'phaseVsFrequency', 
            text: '', 
            align: 'center', 
            headerAlign: 'center', 
            sort: false,
            screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl']
        },
        { dataField: 'action', text: '', align: 'right', headerAlign: 'right', sort: false }
    ];

    const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

    const projectData = sessionDisplay.sessionPulsars.edges.reduce((result, edge) => {
        if (result.filter((project) => project.title === edge.node.project).length === 0) {
            return [
                ...result, 
                { 
                    title: edge.node.project, 
                    value: sessionDisplay.sessionPulsars.edges.filter(
                        (newEdge) => newEdge.node.project === edge.node.project
                    ).length 
                }
            ];
        }

        return result;
    }, []);

    const summaryData = [
        { title: 'Observations', value: sessionDisplay.numberOfObservations },
        { title: 'Pulsars', value: sessionDisplay.numberOfPulsars },
        ...projectData
    ]; 

    return(
        <div className="session-table">
            <h5 style={{ marginTop: '-12rem', marginBottom: '10rem' }}>{startDate} UTC - {endDate} UTC</h5>
            <DataView
                summaryData={summaryData}
                columns={columnsSizeFiltered}
                rows={rows}
                project={project}
                setProject={setProject}
                card={SessionCard}/>
            {isLightBoxOpen && 
            <LightBox
                mainSrc={lightBoxImages.images[lightBoxImages.imagesIndex]}
                nextSrc={lightBoxImages.images[(lightBoxImages.imagesIndex + 1) % lightBoxImages.images.length]}
                prevSrc={
                    lightBoxImages.images[(
                        lightBoxImages.imagesIndex + lightBoxImages.images.length - 1) % lightBoxImages.images.length]}
                onCloseRequest={() => setIsLightBoxOpen(false)}
                onMovePrevRequest={() =>
                    setLightBoxImages({
                        images: lightBoxImages.images,
                        imagesIndex: (
                            lightBoxImages.imagesIndex + lightBoxImages.images.length - 1
                        ) % lightBoxImages.images.length,
                    })
                }
                onMoveNextRequest={() =>
                    setLightBoxImages({
                        images: lightBoxImages.images,
                        imagesIndex: (lightBoxImages.imagesIndex + 1) % lightBoxImages.images.length,
                    })
                }
            />
            }

        </div>
    );
};

export default createRefetchContainer(
    SessionTable,
    {
        data: graphql`
          fragment SessionTable_data on Query @argumentDefinitions(
              start: {type:"String"},
              end: {type:"String"},
              utc: {type:"String"},
              project: {type:"String", defaultValue: "All"}
          ) {
            sessionDisplay(start: $start, end: $end, utc: $utc) {
              start 
              end
              numberOfObservations
              numberOfPulsars
              sessionPulsars(project: $project){
              edges {
                node {
                  jname
                  pulsarType
                  project
                  utc
                  beam
                  integrations
                  frequency
                  backendSN
                  profileHi
                  phaseVsTimeHi
                  phaseVsFrequencyHi
                  profileLo
                  phaseVsTimeLo
                  phaseVsFrequencyLo
                }
                }
              }
            }
          }`
    },
    graphql`
      query SessionTableRefetchQuery($start: String, $end: String, $utc: String, $project: String) {
          ...SessionTable_data @arguments(start: $start, end: $end, utc: $utc, project: $project)
      }
   `
);
