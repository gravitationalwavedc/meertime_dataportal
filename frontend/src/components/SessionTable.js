import { Button, ButtonGroup, Image } from 'react-bootstrap';
import React, { useEffect, useState } from 'react';
import { columnsSizeFilter, formatUTC } from '../helpers';

import DataView from './DataView';
import LightBox from 'react-image-lightbox';
import Link from 'found/Link';
import SessionCard from './SessionCard';
import image404 from '../assets/images/image404.png';
import moment from 'moment';
import { useScreenSize } from '../context/screenSize-context';

// import { createRefetchContainer, graphql } from 'react-relay';


// real props is { data: { relaySessions }, relay }
const SessionTable = () => {
    // Mock data to keep component working
    const relay = { refetch:{} };
    const relaySessions = { edges: [] };

    const { screenSize } = useScreenSize();
    const [project, setProject] = useState('meertime');
    const [isLightBoxOpen, setIsLightBoxOpen] = useState(false);
    const [lightBoxImages, setLightBoxImages] = useState({ images: [], imagesIndex: 0 });

    useEffect(() => {
        relay.refetch({ getProposalFilters: project });
    }, [project, relay]);

    const startDate = moment.parseZone(relaySessions.first, moment.ISO_8601).format('h:mma DD/MM/YYYY');
    const endDate = moment.parseZone(relaySessions.last, moment.ISO_8601).format('h:mma DD/MM/YYYY');

    const openLightBox = (images, imageIndex) => {
        setIsLightBoxOpen(true);
        setLightBoxImages({ images: images, imagesIndex: imageIndex });
    };

    const rows = relaySessions.edges.reduce((result, edge) => { 
        const row = { ...edge.node };
        row.utc = formatUTC(row.utc);
        row.projectKey = project;
        row.length = `${row.length} [s]`;
        row.frequency= `${row.frequency} MHz`;
        
        const images = [
            `${process.env.REACT_APP_MEDIA_URL}${row.profile}`,
            `${process.env.REACT_APP_MEDIA_URL}${row.phaseVsTime}`,
            `${process.env.REACT_APP_MEDIA_URL}${row.phaseVsFrequency}`
        ];

        row.profile = row.profile.length ? 
            <Image rounded onClick={() => openLightBox(images, 0)} fluid src={images[0]}/> : 
            <Image rounded fluid src={image404}/>;
        row.phaseVsTime = row.phaseVsTime.length ?
            <Image rounded onClick={() => openLightBox(images, 1)} fluid src={images[1]}/> : 
            <Image rounded fluid src={image404}/>;
        row.phaseVsFrequency = row.phaseVsFrequency.length ? 
            <Image rounded onClick={() => openLightBox(images, 1)} fluid src={images[2]}/> : 
            <Image rounded fluid src={image404}/>;
        row.action = <ButtonGroup vertical>
            <Link 
                to={`${process.env.REACT_APP_BASE_URL}/fold/${project}/${row.jname}/`} 
                size='sm' 
                variant="outline-secondary" as={Button}>
                  View
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
        { dataField: 'proposalShort', text: 'Project', sort: true, screenSizes: ['md', 'lg', 'xl', 'xxl'] },
        { dataField: 'utc', text: 'UTC', sort: true, screenSizes: ['xl', 'xxl'] },
        { dataField: 'snrSpip', text: 'Backend S/N', align: 'right', headerAlign: 'right', sort: true, 
            screenSizes: ['xl', 'xxl'] },
        { dataField: 'length', text: 'Integration', align: 'right', headerAlign: 'right', sort: true,
            screenSizes: ['xl', 'xxl'] },
        { dataField: 'frequency', text: 'Frequency', align: 'right', headerAlign: 'right', sort: true, 
            screenSizes: ['xxl'] },
        { dataField: 'profile', text: 'Profile', align: 'center', headerAlign: 'center', sort: false },
        { dataField: 'phaseVsTime', text: 'Phase vs time', align: 'center', headerAlign: 'center', sort: false, 
            screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl'] },
        { 
            dataField: 'phaseVsFrequency', 
            text: 'Phase vs frequency', 
            align: 'center', 
            headerAlign: 'center', 
            sort: false,
            screenSizes: ['sm', 'md', 'lg', 'xl', 'xxl']
        },
        { dataField: 'action', text: '', align: 'center', headerAlign: 'center', sort: false }
    ];

    const columnsSizeFiltered = columnsSizeFilter(columns, screenSize);

    const summaryData = [
        { title: 'Observations', value: relaySessions.nobs },
        { title: 'Pulsars', value: relaySessions.npsr },
        ...relaySessions.proposals.map(x => ({ title: x.name, value: x.count }))
    ]; 

    return(
        <div className="session-table">
            <h5 style={{ marginTop: '-12rem', marginBottom: '10rem' }}>{startDate} - {endDate}</h5>
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

export default SessionTable;
// export default createRefetchContainer(
//     SessionTable,
//     {
//         data: graphql`
//           fragment SessionTable_data on Query @argumentDefinitions(
//             getProposalFilters: {type: "String", defaultValue: "meertime"}
//           ) {
//             relaySessions(getProposalFilters: $getProposalFilters) {
//               first
//               last
//               nobs
//               npsr
//               proposals {
//                 name
//                 count
//               }
//               edges {
//                 node {
//                   jname
//                   utc
//                   proposalShort
//                   snrSpip
//                   length
//                   beam
//                   frequency
//                   profile
//                   phaseVsTime
//                   phaseVsFrequency
//                 }
//               }
//             }
//           }`
//     },
//     graphql`
//       query SessionTableRefetchQuery($getProposalFilters: String) {
//         ...SessionTable_data@arguments(getProposalFilters:$getProposalFilters)
//       }
//    `
// );
