import {
    CartesianGrid,
    Label,
    Legend,
    Tooltip,
    XAxis,
    YAxis,
    ZAxis,
} from 'recharts';
import React from 'react';
import ZoomPlot from './ZoomPlot';
import moment from 'moment';
import { snrPlotData } from './plotData';

const SNRPlot= ({ data, columns, search, maxPlotLength }) => {
    const { lBandData, UHFData } = snrPlotData(data, columns, search, maxPlotLength);

    const toolTipFormatter = (value, name) => {
        if (name === 'UTC') {
            return [moment(value).format('DD-MM-YYYY-hh:mm:ss'), name];
        }
        
        if (name === 'Size') {
            return [`${value} [m]`, 'Integration time'];
        }

        return [value, name];
    };

    return (
        <ZoomPlot dataOne={lBandData} dataTwo={UHFData}>
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
            <Tooltip cursor={{ strokeDasharray: '3 3' }} formatter={toolTipFormatter} />
            <Legend 
                align="right" 
                verticalAlign="top"
                payload={[
                    { id:'1', type: 'circle', value: 'L-Band', color: '#8884d8' },
                    { id:'1', type: 'square', value: 'UHF', color: '#e07761' }
                ]}
            />
        </ZoomPlot>
    );
};

export default SNRPlot;
