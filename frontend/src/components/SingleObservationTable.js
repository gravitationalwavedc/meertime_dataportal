import { Button, Col, Row } from 'react-bootstrap';
import { formatUTC, kronosLink } from '../helpers';

import DataDisplay from './DataDisplay';
import ImageGrid from './ImageGrid';
import Link from 'found/Link';
import MainLayout from './MainLayout';
import React from 'react';


const titles = [
    'jname',
    'beam',
    'utc'
];

const SingleObservationTable = ({ data: { foldObservationDetails }, jname }) => {
    const relayObservationModel = foldObservationDetails.edges[0].node;
    const title = <Link
        size="sm"
        to={`${process.env.REACT_APP_BASE_URL}/fold/meertime/${jname}/`}>
        {jname} 
    </Link>;
    const displayDate = formatUTC(relayObservationModel.utc);

    const dataItems = Object.keys(relayObservationModel)
        .filter(key => !titles.includes(key) && key !== 'images')
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
                </Col>
            </Row>
            <Row className="single-observation-data">
                <ImageGrid images={relayObservationModel.images} />
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
