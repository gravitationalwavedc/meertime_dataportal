import {
    CartesianGrid,
    Label,
    Legend,
    ReferenceArea,
    ResponsiveContainer,
    Scatter,
    ScatterChart,
    Tooltip,
    XAxis,
    YAxis,
    ZAxis,
} from 'recharts';
import React, { useState } from 'react';
import { fluxPlotData } from './plotData';
import moment from 'moment';
import { useRouter } from 'found';


const FluxPlot = ({ data, columns, search, maxPlotLength }) => {
    const [ zoomArea, setZoomArea ] = useState({ x1: null, y1: null, x2: null, y2: null });
    const [isZooming, setIsZooming] = useState(false);

    const { lBandData, UHFData } = fluxPlotData(data, columns, search, maxPlotLength);
    const { router } = useRouter();

    const handleSymbolClick = (symbolData) => { 
        router.push(symbolData.link);
    };

    const handleMouseDown = (e) => {
        setIsZooming(true);
        const { xValue, yValue } = e || {};
        setZoomArea({ x1: xValue, y1: yValue, x2: xValue, y2: yValue });
    };

    const handleMouseMove = (e) => {
        if(isZooming) {
            setZoomArea((prev) => ({ ...prev, x2: e ? e.xValue : null, y2: e ? e.yValue : null }));
        }
    };

    const handleMouseUp = (e) => {
        setIsZooming(false);
        let { x1, y1, x2, y2 } = zoomArea;
        
        // ensure x1 <= x2 and y1 <= y2
        if (x1 > x2) [x1, x2] = [x2, x1];
        if (y1 > y2) [y1, y2] = [y2, y1];
        
        // setZoomArea({ x1: null, y1: null, x2: null, y2: null });
    };

    return (
        <ResponsiveContainer>
            <ScatterChart
                margin={{
                    top: 20,
                    right: 20,
                    bottom: 20,
                    left: 20,
                }}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
            >
                <CartesianGrid />
                <XAxis 
                    type="number" 
                    dataKey="time" 
                    name="UTC" 
                    tickCount={8}
                    domain={['auto', 'auto']} 
                    tickFormatter={(unixTime) => moment(unixTime).format('DD/MM/YY')}>
                    <Label value="UTC" position="bottom"/>
                </XAxis>
                <YAxis type="number" dataKey="value" name="Flux">
                    <Label value="Flux Density" position="left" angle="-90"/>
                </YAxis>
                <ZAxis type="number" dataKey="size" name="Size" range={[60, 400]} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend 
                    align="right" 
                    verticalAlign="top"
                    payload={[
                        { id:'1', type: 'circle', value: 'L-Band', color: '#8884d8' },
                        { id:'1', type: 'square', value: 'UHF', color: '#e07761' }
                    ]}
                />
                <Scatter name="L-Band" data={lBandData} fill="#8884d8" shape="circle" onClick={handleSymbolClick} />
                <Scatter name="UHF" data={UHFData} fill="#e07761" shape="square" onClick={handleSymbolClick} />
                <ReferenceArea
                    x1={zoomArea.x1 ? zoomArea.x1 : null}
                    x2={zoomArea.x2 ? zoomArea.x2 : null}
                    y1={zoomArea.y1 ? zoomArea.y1 : null}
                    y2={zoomArea.y2 ? zoomArea.y2 : null}
                />
            </ScatterChart>
        </ResponsiveContainer>
    );
};

export default FluxPlot;
