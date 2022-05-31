import {
    ChartLabel,
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

import moment from 'moment';
import { pulsarSummaryPlotData } from './plotData';
import { useRouter } from 'found';


const PulsarSummaryPlot = ({ data, columns, search, maxPlotLength }) => { 
    const [value, setValue] = useState(false);
    const [lastDrawLocation, setLastDrawLocation] = useState(null);
    const { router } = useRouter();

    const plotData = pulsarSummaryPlotData(
        data, 
        columns, 
        search, 
        lastDrawLocation, 
        setLastDrawLocation, 
        maxPlotLength, 
    );

    const plotLink = () => {
        router.replace(value.link);
    };

    return (
        <FlexibleXYPlot 
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
                                { title: value.type, value: value.y },
                                { title: 'integration time', value: `${value.length} [m]` },
                                { title: 'UTC', value: value.x.format('YYYY-MM-DD-HH:mm:ss') }
                            ]} 
                        />
            }
            <CustomSVGSeries 
                data={plotData} 
                animation={true}
                onNearestXY={value => setValue(value)}/>
            <ChartLabel 
                text="UTC"
                className="x-axis-label"
                includeMargin={true}
                xPercent={0.5}
                yPercent={0.73}/>
            <ChartLabel 
                text="S/N"
                className="y-axis-label"
                includeMargin={true}
                xPercent={0.04}
                yPercent={0.5}
                style={{
                    transform: 'rotate(-90)',
                }}
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
    );
};

export default PulsarSummaryPlot;
