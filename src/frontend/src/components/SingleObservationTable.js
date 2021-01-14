import { Button, Col, Image, Row } from 'react-bootstrap';
import { formatUTC, kronosLink } from '../helpers';

import DataDisplay from './DataDisplay';
import Link from 'found/Link';
import MainLayout from './MainLayout';
import React from 'react';
import image404 from '../assets/images/image404.png';

const imageNames = [
    'profile',
    'bandpass',
    'phaseVsTime',
    'phaseVsFrequency',
    'snrVsTime'
];

const titles = [
    'jname',
    'beam',
    'utc'
];

const SingleObservationTable = ({ data: { relayObservationModel } }) => {
    const title = `${relayObservationModel.jname}`;  
    const displayDate = formatUTC(relayObservationModel.utc);

    const pulsarImages = Object.keys(relayObservationModel)
        .filter(key => imageNames.includes(key))
        .reduce((result, key) => ({ ...result, [key]: relayObservationModel[key] }), {});

    const dataItems = Object.keys(relayObservationModel)
        .filter(key => !imageNames.includes(key) && !titles.includes(key))
        .reduce((result, key) => ({ ...result, [key]: relayObservationModel[key] }), {});

    return (
        <MainLayout title={title}>
            <h5 style={{ marginTop: '-12rem' }}>{displayDate}</h5>
            <h5>Beam {relayObservationModel.beam}</h5>
            <Row>
                <Col>
                    <Button 
                        size="sm"
                        as="a"
                        className="mr-2"
                        href={kronosLink(
                            relayObservationModel.beam,
                            relayObservationModel.jname,
                            displayDate
                        )}
                        variant="outline-secondary"> 
                      View Kronos
                    </Button>
                    <Link
                        size="sm"
                        as={Button}
                        to={`/fold/meertime/${title}/`}
                        variant="outline-secondary"> 
                      View {relayObservationModel.jname} 
                    </Link>
                </Col>
            </Row>
            <Row className="mt-3">
                <Col>
                    {Object.keys(pulsarImages).map(key => <Image 
                        rounded
                        fluid
                        key={key}
                        className="mb-3"
                        alt={key}
                        src={pulsarImages[key].length > 0 ? `http://localhost:8000/media/${pulsarImages[key]}` : image404}/>                     )}
                </Col>
                <Col>
                    {Object.keys(dataItems).map(key => 
                        <DataDisplay key={key} title={key} value={dataItems[key]} /> 
                    )}
                </Col>
            </Row>
        </MainLayout>
    );
};

export default SingleObservationTable;
