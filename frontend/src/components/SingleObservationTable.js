import { Button, Col, Form, Row } from 'react-bootstrap';
import React, { useState } from 'react';
import { formatUTC, kronosLink } from '../helpers';

import DataDisplay from './DataDisplay';
import ImageGrid from './ImageGrid';
import Link from 'found/Link';
import MainLayout from './MainLayout';
import { formatSingleObservationData } from '../helpers';


const SingleObservationTable = ({ data: { foldObservationDetails }, jname }) => {
    const [ project, setProject ] = useState('relbin');

    const relayObservationModel = foldObservationDetails.edges[0].node;

    const title = <Link
        size="sm"
        to={`${process.env.REACT_APP_BASE_URL}/fold/meertime/${jname}/`}>
        {jname}
    </Link>;

    const displayDate = formatUTC(relayObservationModel.utc);

    const dataItems = formatSingleObservationData(relayObservationModel);

    const projects = Array.from(relayObservationModel.images.edges.reduce(
        (plotTypesSet, { node }) => plotTypesSet.add(node.process.toUpperCase()), new Set()
    )).filter(process => process !== 'RAW');

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
            {projects.length > 1 ? 
                <Row className="mt-2">
                    <Col md={2}>
                        <Form.Group controlId="mainProjectSelect">
                            <Form.Label>Cleaned Data Project</Form.Label>
                            <Form.Control 
                                custom
                                as="select"  
                                value={project}
                                onChange={(event) => setProject(event.target.value)}>
                                {projects.map(
                                    value => 
                                        <option 
                                            value={value}
                                            key={value}>
                                            {value}
                                        </option>)
                                }
                            </Form.Control>
                        </Form.Group>
                    </Col>
                </Row>
                : null}
            <Row className="single-observation-data">
                <ImageGrid images={relayObservationModel.images} project={project} />
                <Col md={8} xl={6}>
                    {Object.keys(dataItems).map(key =>
                        <DataDisplay key={key} title={key} value={dataItems[key]} full />
                    )}
                </Col>
            </Row>
        </MainLayout>
    );
};

export default SingleObservationTable;
