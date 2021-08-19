import {
    CustomSVGSeries,
    FlexibleXYPlot,
    Highlight,
    Hint,
    HorizontalGridLines,
    VerticalGridLines,
    XAxis,
    YAxis
} from 'react-vis';
import React, { useState } from 'react';

import { Col } from 'react-bootstrap';
import { HiOutlineQuestionMarkCircle } from 'react-icons/hi';
import { handleSearch } from '../helpers';
import moment from 'moment';
import { useRouter } from 'found';

const scaleValue = (value, from, to) => {
    const scale = (to[1] - to[0]) / (from[1] - from[0]);
    const capped = Math.min(from[1], Math.max(from[0], value)) - from[0];
    return ~~(capped * scale + to[0]);
};

const getPlotData = (data, columns, search, lastDrawLocation, setLastDrawLocation, maxPlotLength, minPlotLength) => {
    // Pass table data through the search filter to enable searching pulsars on chart.
    const results = search.searchText ? handleSearch(data, columns, search) : data;

    // Process the table data in a way that react-vis understands.
    const plotData = results.map(row => ({ 
        x: moment(row.utc, 'YYYY-MM-DD-HH:mm:ss'), 
        y: row.snBackend,
        value: row.snBackend,
        customComponent: row.band === 'L-BAND' ? 'circle' : 'square',
        style: { fill:'#E07761', opacity:'0.4' },
        size: scaleValue(row.length, [minPlotLength, maxPlotLength], [5, 500]),
        color: '#E07761',
        length: row.length,
        link: row.plotLink
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

const PulsarSummaryPlot = ({ data, columns, search, maxPlotLength, minPlotLength }) => { 
    const [value, setValue] = useState(false);
    const [lastDrawLocation, setLastDrawLocation] = useState(null);
    const { router } = useRouter();

    const plotData = getPlotData(
        data, 
        columns, 
        search, 
        lastDrawLocation, 
        setLastDrawLocation, 
        maxPlotLength, 
        minPlotLength
    );

    const plotLink = () => {
        router.replace(value.link);
    };

    return (
        <Col md={10} className="pulsar-plot-display">
            <p className="text-muted pt-3">
                <HiOutlineQuestionMarkCircle className="mb-1" /> 
                Drag to zoom. Click empty area to reset. Double click to view utc.
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
                    onDoubleClick={plotLink}
                    className="m-5" 
                >
                    <VerticalGridLines xType="time" tickTotal={5} />
                    <HorizontalGridLines />
                    <XAxis 
                        xType="time-utc"
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
                                { title: 'integration time', value: `${value.length} [m]` },
                                { title: 'UTC', value: value.x.format('YYYY-MM-DD-HH:mm:ss') }
                            ]} 
                        />
                    }
                    <CustomSVGSeries 
                        data={plotData} 
                        animation={true}
                        onNearestXY={value => setValue(value)}/>
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
        </Col>
    );
};

export default PulsarSummaryPlot;
