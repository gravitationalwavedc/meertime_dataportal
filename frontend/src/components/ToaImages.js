import { Col, Row } from 'react-bootstrap';
import PlotImage from './PlotImage';
import React from 'react';

const ToaImages = ({ processedImages, handleLightBox }) => {

    const toaGlobal = processedImages.find(image => image.node.plotType === 'toa-global');

    return <Row className="mb-5">
        {toaGlobal &&
        <Col>
            <PlotImage
                imageData={toaGlobal.node}
                handleClick={() => handleLightBox(toaGlobal.node.url)} />
        </Col>
        }
    </Row>;
};

export default ToaImages;