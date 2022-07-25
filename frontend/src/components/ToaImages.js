import { Col, Row } from 'react-bootstrap';
import PlotImage from './PlotImage';
import React from 'react';

const ToaImages = ({ processedImages, handleLightBox }) => {

    const toaGlobal = processedImages.find(image => image.node.plotType === 'toa-global');
    const toaSingle = processedImages.find(image => image.node.plotType === 'toa-single');
    return <Row>
        {toaGlobal &&
        <Col sm={6} md={2} xl={3}>
            <PlotImage
                imageData={toaGlobal.node}
                handleClick={() => handleLightBox(toaGlobal.node.url)} />
        </Col>
        }
        {toaSingle &&
        <Col sm={6} md={2} xl={3}>
            <PlotImage
                imageData={toaSingle.node}
                handleClick={() => handleLightBox(toaSingle.node.url)} />
        </Col>
        }
    </Row>;
};

export default ToaImages;