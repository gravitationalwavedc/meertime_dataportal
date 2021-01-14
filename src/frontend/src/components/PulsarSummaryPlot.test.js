import PulsarSummaryPlot from './PulsarSummaryPlot';
import React from 'react';
import { render } from '@testing-library/react';

describe('pulsar Summary Plot component', () => {

    it('should render a circle for each data point', () => {
        expect.hasAssertions();
        const data = [{
            band: 'L-band',
            beam: 4,
            bw: 856,
            dmFold: 314,
            dmPipe: null,
            id: 'T2JzZXJ2YXRpb25EZXRhaWxOb2RlOjE4MDgz',
            key: '2020-09-29-17:13:32:4',
            length: 5,
            nant: 58,
            nantEff: 58,
            nbin: 1024,
            nchan: 1024,
            proposalShort: 'TPA',
            rmPipe: null,
            snrPipe: null,
            snrSpip: 38.7,
            utc: '2020-09-29-17:13:32'
        }];
        const { container } = render(
            <PulsarSummaryPlot search={{ searchText: '' }} data={data} />
        ); 
        expect(container.querySelector('circle')).not.toBeNull();
    }); 
});
