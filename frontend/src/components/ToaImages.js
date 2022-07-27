import { Col, Row } from 'react-bootstrap';
import PlotImage from './PlotImage';
import React from 'react';

const ToaImages = ({ processedImages, handleLightBox }) => {

    const toaGlobal = processedImages.find(image => image.node.plotType === 'toa-global');
    const toaSingle = processedImages.find(image => image.node.plotType === 'toa-single');

    return <Row className="mb-5">
        {toaGlobal &&
        <Col>
            <PlotImage
                imageData={toaGlobal.node}
                handleClick={() => handleLightBox(toaGlobal.node.url)} />
        </Col>
        }
        {toaSingle &&
        <Col>
            <PlotImage
                imageData={toaSingle.node}
                handleClick={() => handleLightBox(toaSingle.node.url)} />
        </Col>
        }
    </Row>;
};

export default ToaImages;