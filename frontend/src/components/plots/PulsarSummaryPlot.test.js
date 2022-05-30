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
            id: '1',
            utc: '2020-02-04-00:21:21',
            project: 'Relbin',
            length: 13.4,
            beam: 1,
            bw: 775.75,
            nchan: 928,
            band: 'UHF',
            nbin: 1024,
            nant: 53,
            nantEff: 53,
            dmFold: -1,
            dmMeerpipe: null,
            rmMeerpipe: null,
            snBackend: 134.5,
            snMeerpipe: null,
            key: '2020-02-04T00:21:21+00:00:1',
            jname: undefined,
            plotLink: '/undefined/2020-02-04-00:21:21/1/'
        }];

        const { container } = render(
            <PulsarSummaryPlot search={{ searchText: '' }} data={data} columns={{}} />
        ); 
        expect(container.querySelector('rect')).not.toBeNull();
    }); 
});
