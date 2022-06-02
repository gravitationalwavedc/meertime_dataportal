import {
    CartesianGrid,
    Label,
    Legend,
    ResponsiveContainer,
    Scatter,
    ScatterChart,
    Tooltip,
    XAxis,
    YAxis,
    ZAxis,
} from 'recharts';
import React from 'react';
import { fluxPlotData } from './plotData';
import moment from 'moment';
import { useRouter } from 'found';

const FluxPlot = ({ data, columns, search, maxPlotLength }) => {
    const { lBandData, UHFData } = fluxPlotData(data, columns, search, maxPlotLength);
    const { router } = useRouter();

    const handleSymbolClick = (symbolData) => { 
        router.push(symbolData.link);
    };

    return (
        <ResponsiveContainer width="100%" height="100%">
            <ScatterChart
                margin={{
                    top: 20,
                    right: 20,
                    bottom: 20,
                    left: 20,
                }}
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
            </ScatterChart>
        </ResponsiveContainer>
    );
};

export default FluxPlot;
