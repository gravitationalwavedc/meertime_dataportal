import { Button, Col, Image, Row } from 'react-bootstrap';
import { formatUTC, kronosLink } from '../helpers';

import DataDisplay from './DataDisplay';
import Link from 'found/Link';
import MainLayout from './MainLayout';
import React from 'react';
import image404 from '../assets/images/image404.png';

const imageNames = [
    'profileHi',
    'bandpassHi',
    'phaseVsTimeHi',
    'phaseVsFrequencyHi',
    'snrVsTimeHi'
];

const titles = [
    'jname',
    'beam',
    'utc'
];

const SingleObservationTable = ({ data: { foldObservationDetails }, jname }) => {
    const relayObservationModel = foldObservationDetails.edges[0].node;
    const title = `${jname}`;  
    const displayDate = formatUTC(relayObservationModel.utc);

    const pulsarImages = Object.keys(relayObservationModel)
        .filter(key => imageNames.includes(key))
        .reduce((result, key) => ({ ...result, [key]: relayObservationModel[key] }), {});

    const dataItems = Object.keys(relayObservationModel)
        .filter(key => !imageNames.includes(key) && !titles.includes(key))
        .reduce((result, key) => ({ ...result, [key]: relayObservationModel[key] }), {});

    return (
        <MainLayout title={title}>
            <h5 className="single-observation-subheading">{displayDate}</h5>
            <h5>Beam {relayObservationModel.beam}</h5>
            <Row>
                <Col>
                    <Button 
                        size="sm"
                        as="a"
                        className="mr-2"
                        href={kronosLink(
                            relayObservationModel.beam,
                            jname,
                            displayDate
                        )}
                        variant="outline-secondary"> 
                      View Kronos
                    </Button>
                    <Link
                        size="sm"
                        as={Button}
                        to={`${process.env.REACT_APP_BASE_URL}/fold/meertime/${title}/`}
                        variant="outline-secondary"> 
                      View {jname} 
                    </Link>
                </Col>
            </Row>
            <Row className="single-observation-data">
                <Col sm={12} md={4} xl={6}>
                    {Object.keys(pulsarImages).map(key => <Image 
                        rounded
                        fluid
                        key={key}
                        className="mb-3"
                        alt={key}
                        src={pulsarImages[key] ? `${process.env.REACT_APP_MEDIA_URL}${pulsarImages[key]}` : image404}/>                     )}
                </Col>
                <Col md={8} xl={6}>
                    {Object.keys(dataItems).map(key => 
                        <DataDisplay key={key} title={key} value={dataItems[key]} full/> 
                    )}
                </Col>
            </Row>
        </MainLayout>
    );
};

export default SingleObservationTable;
