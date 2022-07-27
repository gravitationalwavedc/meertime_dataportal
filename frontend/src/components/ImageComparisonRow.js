import { Col, Row } from 'react-bootstrap';
import PlotImage from './PlotImage';
import React from 'react';


const ImageComparisonRow = ({ sizes, rawImage, processedImage, openLightBox }) => <Row>
    <Col {...sizes}>
        <PlotImage
            imageData={rawImage ? rawImage.node : null} 
            handleClick={() => openLightBox(rawImage.node.url)}
        />
    </Col>
    <Col {...sizes}>
        <PlotImage
            imageData={processedImage ? processedImage.node : null}
            handleClick={() => openLightBox(processedImage.node.url)}
        />
    </Col>
</Row>;

export default ImageComparisonRow;