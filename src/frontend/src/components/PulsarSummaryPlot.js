import {
    FlexibleXYPlot,
    Highlight,
    Hint,
    HorizontalGridLines,
    MarkSeries,
    VerticalGridLines,
    XAxis,
    YAxis
} from 'react-vis';
import React, { useState } from 'react';

import { Col } from 'react-bootstrap';
import { HiOutlineQuestionMarkCircle } from 'react-icons/hi';
import { handleSearch } from '../helpers';
import moment from 'moment';

const getPlotData = (data, columns, search, lastDrawLocation, setLastDrawLocation) => {
    // Pass tqble data through the search filter to enable searching pulsars on chart.
    const results = search.searchText ? handleSearch(data, columns, search) : data;

    // Process the table data in a way that react-vis understands.
    const plotData = results.map(row => ({ 
        x: moment(row.utc, 'YYYY-MM-DD-HH:mm:ss'), 
        y: row.snrSpip,
        size: row.length,
        color: '#E07761'
    }));

    if (plotData.length && plotData.length < 2 && lastDrawLocation === null){
        setLastDrawLocation({
            top: plotData[0].y + 100,
            bottom: plotData[0].y - 100,
            left: plotData[0].x.clone().subtract(3, 'days').toDate(), 
            right: plotData[0].x.clone().add(3, 'days').toDate()
        });
    }

    return plotData;
};

const PulsarSummaryPlot = ({ data, columns, search }) => { const [value, setValue] = useState(false);
    const [lastDrawLocation, setLastDrawLocation] = useState(null);

    const plotData = getPlotData(data, columns, search, lastDrawLocation, setLastDrawLocation);

    return (
        <Col md={10} className="pulsar-plot-display">
            <p className="text-muted pt-3">
                <HiOutlineQuestionMarkCircle className="mb-1" /> Drag to zoom. Click empty area to reset.
            </p>
            <p className="y-label">S/N</p>
            <div className="pulsar-plot-wrapper">
                <FlexibleXYPlot 
                    margin={{ left: 60, right: 60, top: 60, bottom: 60 }}
                    xDomain={
                        lastDrawLocation && [
                            lastDrawLocation.left,
                            lastDrawLocation.right
                        ]
                    }
                    yDomain={
                        lastDrawLocation && [
                            lastDrawLocation.bottom,
                            lastDrawLocation.top
                        ]
                    }
                    onMouseLeave={() => setValue(false)} 
                    className="m-5" 
                >
                    <VerticalGridLines xType="time" tickTotal={5} />
                    <HorizontalGridLines />
                    <XAxis 
                        xType="time"
                        tickTotal={5}
                        tickFormat={(v) => moment(v).format('DD/MM/YY')} 
                    />
                    <YAxis />
                    {
                        value && 
                        <Hint 
                            value={value} 
                            format={(value) => [
                                { title: 'raw S/N', value: value.y },
                                { title: 'integration time [m]', value: value.size },
                                { title: 'UTC', value: value.x.format('YYYY-MM-DD-HH:mm:ss') },
                            ]} 
                        />
                    }
                    <MarkSeries 
                        data={plotData} 
                        seriesId="pulsar-mark-series"
                        sizeRange={[10, 50]} 
                        colorType="literal"
                        opacity={0.4} 
                        animation={true}
                        onNearestXY={value => setValue(value)}
                    />
                    <Highlight
                        onBrushEnd={area => setLastDrawLocation(area)}
                        onDrag={area => setLastDrawLocation({
                            bottom: lastDrawLocation.bottom + (area.top - area.bottom),
                            left: lastDrawLocation.left - (area.right = area.left),
                            right: lastDrawLocation.right - (area.right - area.left),
                            top: lastDrawLocation.top + (area.top - area.bottom)
                        })}/>
                </FlexibleXYPlot>
            </div>
            <p className="pb-4 text-center text-primary-600">UTC</p>
        </Col>);
};

export default PulsarSummaryPlot;
