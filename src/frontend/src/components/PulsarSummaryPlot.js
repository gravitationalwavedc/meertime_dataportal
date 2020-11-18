import React, { useState } from 'react';
import moment from 'moment'; 
import { Highlight, Hint, XAxis, YAxis, XYPlot, MarkSeries, VerticalGridLines, HorizontalGridLines } from 'react-vis';
import { handleSearch } from '../helpers';


const PulsarSummaryPlot = ({ data, columns, search }) => {
    const [value, setValue] = useState(false);
    const [lastDrawLocation, setLastDrawLocation] = useState(null);

    const results = search.searchText ? handleSearch(data, columns, search) : data;

    const plotData = results.map(row => ({ 
        x: moment(row.utc, 'YYYY-MM-DD-HH:mm:ss'), 
        y: row.snrSpip,
        size: row.length
    }));

    return (
        <React.Fragment>
            <XYPlot 
                margin={{ left: 60, right: 60, top: 40, bottom: 40 }}
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
                width={1000} 
                height={500}>
                <VerticalGridLines />
                <HorizontalGridLines />
                <XAxis 
                    tickTotal={5}
                    xType="time"
                    title="UTC"
                    tickFormat={
                        (v) => moment(v).format('MM/YYYY')
                    } />
                <YAxis title="S/N"/>
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
                    opacity={0.5} 
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
            </XYPlot>
        </React.Fragment>);
};

export default PulsarSummaryPlot;
