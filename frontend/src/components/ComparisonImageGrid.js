import { Col, Row } from 'react-bootstrap';
import ImageComparisonRow from './ImageComparisonRow';
import PlotImage from './PlotImage';
import React from 'react';
import { formatProjectName } from '../helpers';

const ComparisonImageGrid = ({ rawImages, processedImages, openLightBox, project }) => {
    const comparisonImageTypes = [
        { rawType:'flux', processedType: 'flux' }, 
        { rawType:'freq', processedType: 'freq' }, 
        { rawType:'time', processedType: 'time' },
        { rawType:'band', processedType: 'bandpass' }, 
        { rawType:'snrt', processedType: 'snr-cumul' }
    ];
    
    const extraImageOrder = ['calib-dynspec', 'profile-pol', 'snr-single', 'toa-single', 'zap-dynspec'];

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
        {processedImages.length > 0 && 
            <React.Fragment>
                <Row className="mt-5">
                    <Col>
                        <h5>
                            Cleaned by {formatProjectName(project)}
                        </h5>
                    </Col>
                </Row>
                <Row>
                    <Col>
                        {extraImageOrder.map(imageType => {
                            const edge = processedImages.find(({ node }) => node.plotType === imageType);
                            if(edge === undefined) return null;
                            return <PlotImage 
                                key={imageType}
                                imageData={edge.node}
                                handleClick={() => openLightBox(edge.node.url)} 
                            />;
                        })}
                    </Col>
                </Row>
            </React.Fragment>
        }
    </React.Fragment>;
};

export default ComparisonImageGrid;