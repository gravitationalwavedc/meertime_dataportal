import React, { useState } from 'react';
import { Col } from 'react-bootstrap';
import FluxPlot from './FluxPlot';
import Form from 'react-bootstrap/Form';
import SNRPlot from './newPlot';

const PlotContainer = ({ maxPlotLength, ...rest }) => {
    const [activePlot, setActivePlot] = useState('flux');

    return <Col md={10} className="pulsar-plot-display">
        <Form.Row>
            <Form.Group controlId="plotController" className="mb-0">
                <Form.Label>Plot Type</Form.Label>
                <Form.Control 
                    custom
                    as="select"  
                    value={activePlot}
                    onChange={(event) => setActivePlot(event.target.value)}>
                    <option value="flux">Flux Density</option>
                    <option value="snr">S/N</option>
                </Form.Control>
                <Form.Text className="text-muted">
                    Drag to zoom, click empty area to reset, double click to view utc.
                </Form.Text>
            </Form.Group>
        </Form.Row>
        <div className="pulsar-plot-wrapper">
            { activePlot === 'snr' ? 
                <SNRPlot maxPlotLength={maxPlotLength} {...rest} /> :
                <FluxPlot maxPlotLength={maxPlotLength} {...rest} />
            }
        </div>
    </Col>;
};

export default PlotContainer;
