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
import moment from 'moment';
import { snrPlotData } from './plotData';
import { useRouter } from 'found';

const SNRPlot= ({ data, columns, search, maxPlotLength }) => {
    const { lBandData, UHFData } = snrPlotData(data, columns, search, maxPlotLength);
    const { router } = useRouter();

    const handleSymbolClick = (symbolData) => { 
        router.push(symbolData.link);
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
            >
                <CartesianGrid />
                <XAxis 
                    type="number" 
                    dataKey="time"
                    tickCount={8}
                    name="UTC" 
                    domain={['auto', 'auto']} 
                    tickFormatter={(unixTime) => moment(unixTime).format('DD/MM/YY')}>
                    <Label value="UTC" position="bottom"/>
                </XAxis>
                <YAxis type="number" dataKey="value" name="S/N">
                    <Label value="S/N" position="left" angle="-90"/>
                </YAxis>
                <ZAxis type="number" dataKey="size" name="Size" range={[60, 400]} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend 
                    align="right" 
                    verticalAlign="top"
                    payload={[
                        { id:'1', type: 'circle', value: 'L-Band', color: '#8884d8' },
                        { id:'1', type: 'square', value: 'UHF', color: '#82ca9d' }
                    ]}
                />
                <Scatter name="L-Band" data={lBandData} fill="#8884d8" shape="circle" onClick={handleSymbolClick} />
                <Scatter name="UHF" data={UHFData} fill="#82ca9d" shape="square" onClick={handleSymbolClick} />
            </ScatterChart>
        </ResponsiveContainer>
    );
};

export default SNRPlot;
