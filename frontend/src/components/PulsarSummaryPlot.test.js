import PulsarSummaryPlot from './PulsarSummaryPlot';
import React from 'react';
import { render } from '@testing-library/react';

/* eslint-disable react/display-name */

jest.mock('found', () => ({
    Link: component => <div>{component.children}</div>,
    useRouter: () => ({ router: {
        push: jest.fn(),
        replace: jest.fn(),
        go: jest.fn(),
        createHref: jest.fn(),
        createLocation: jest.fn(),
        isActive: jest.fn(),
        matcher: {
            match: jest.fn(),
            getRoutes: jest.fn(),
            isActive: jest.fn(),
            format: jest.fn()
        },
        addTransitionHook: jest.fn()
    } }) 
}));

describe('pulsar Summary Plot component', () => {

    it('should render a circle for each data point', () => {
        expect.hasAssertions();
        const data = [{
            action: {},
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
            <PulsarSummaryPlot search={{ searchText: '' }} data={data} columns={{}} />
        ); 
        expect(container.querySelector('circle')).not.toBeNull();
    }); 
});
