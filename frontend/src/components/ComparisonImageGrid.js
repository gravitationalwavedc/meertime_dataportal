import { Col, Row } from 'react-bootstrap';
import ImageComparisonRow from './ImageComparisonRow';
import PlotImage from './PlotImage';
import React from 'react';
import { formatProjectName } from '../helpers';

const ComparisonImageGrid = ({ rawImages, processedImages, openLightBox, project }) => {
    const comparisonImageTypes = [
        { rawType:'band', processedType: 'bandpass' }, 
        { rawType:'freq', processedType: 'freq' }, 
        { rawType:'flux', processedType: 'flux' }, 
        { rawType:'snrt', processedType: 'snr-cumul' }, 
        { rawType:'time', processedType: 'time' }
    ];
    const toaImageTypes = ['toa-global', 'toa-single'];

    return <React.Fragment>
        <Row>
            <Col>
                <h5>Raw</h5> 
            </Col>
            <Col>
                <h5>
                    Cleaned by {formatProjectName(project)}
                </h5>
            </Col> 
        </Row>
        {comparisonImageTypes.map(({ rawType, processedType }) =>
            <ImageComparisonRow 
                key={`${rawType}_${processedType}`}
                rawImage={rawImages.find(({ node }) => node.plotType === rawType)}
                processedImage={processedImages.find(({ node }) => node.genericPlotType === processedType)}
                openLightBox={openLightBox}
            />
        )}
        <Row>
            <Col/>
            {processedImages.length > 0 && <Col>
                {processedImages
                    .filter(({ node }) => !toaImageTypes.includes(node.genericPlotType))
                    .filter(
                        ({ node }) => !comparisonImageTypes.some(
                            imageType => imageType.processedType === node.genericPlotType
                        )
                    )
                    .map(({ node }) =>
                        <PlotImage 
                            key={node.url}
                            imageData={node}
                            handleClick={() => openLightBox(node.url)} 
                        />
                    )}
            </Col>}
        </Row>
    </React.Fragment>;
};

export default ComparisonImageGrid;