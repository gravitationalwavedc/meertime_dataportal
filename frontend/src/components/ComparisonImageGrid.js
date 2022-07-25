import { Col, Row } from 'react-bootstrap';
import PlotImage from './PlotImage';
import React from 'react';
import { formatProjectName } from '../helpers';

const ComparisonImageGrid = ({ rawImages, processedImages, openLightBox, project }) => {
    const sizes = processedImages.length > 0 ? { sm: 6, md: 2, xl: 3 } : { sm: 12, md: 4, xl: 6 };
    const comparisonImageTypes = ['bandpass', 'freq', 'time', 'flux', 'snrt'];

    const rawBand = rawImages.find(({ node }) => node.plotType === 'band');
    const processedBand = processedImages.find(({ node }) => node.genericPlotType === 'bandpass');

    console.log(rawImages);

    return <React.Fragment>
        <Row>
            <Col {...sizes}>
                <h4>Raw</h4> 
            </Col>
            <Col {...sizes}>
                <h4>
                    Cleaned by {formatProjectName(project)}
                </h4>
            </Col>
        </Row>
        <Row>
            <Col {...sizes}>
                <PlotImage
                    imageData={rawBand ? rawBand.node : null} 
                    handleClick={() => openLightBox(rawBand.node.url)}
                />
            </Col>
            <Col {...sizes}>
                <PlotImage
                    imageData={processedBand ? processedBand.node : null}
                    handleClick={() => openLightBox(processedBand.node.url)}
                />
            </Col>
        </Row>
        <Row>
            <Col {...sizes}>
                <h4>Raw</h4>
                {rawImages.sort().map(({ node }) =>
                    <PlotImage
                        key={node.url}
                        imageData={node}
                        handleClick={() => openLightBox(node.url)}
                    />
                )}
            </Col>
            {processedImages.length > 0 && <Col sm={6} md={2} xl={3}>
                <h4>Cleaned by {formatProjectName(project)}</h4>
                {processedImages
                    .filter(({ node }) => comparisonImageTypes.includes(node.genericPlotType))
                    .sort()
                    .map(({ node }) =>
                        <PlotImage 
                            key={node.url}
                            imageData={node}
                            handleClick={() => openLightBox(node.url)} 
                        />
                    )}
            </Col>}
        </Row>
    </React.Fragment>
    ;
};

export default ComparisonImageGrid;