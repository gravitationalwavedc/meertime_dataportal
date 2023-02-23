import { render, screen } from '@testing-library/react';
import ObservationTimeView from './SingleObservationTable';
import React from 'react';

/* eslint-disable react/display-name */

jest.mock('found', () => ({
    Link: component => <div>{component.children}</div>,
    useRouter: () => ({
        router: {
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
        }
    })
}));

jest.mock('found/Link', () => ({ children }) => <div>{children}</div>);

describe('observationTimeView component', () => {

    it('should render the page with images', () => {
        expect.hasAssertions();
        const data = {
            foldObservationDetails: {
                edges: [
                    {
                        node: {
                            beam: 1,
                            utc: '2020-02-04T00:21:21+00:00',
                            project: 'meertime',
                            proposal: 'SCI-20180516-MB-02',
                            frequency: 1283.582031,
                            bw: 775.75,
                            ra: '14:24:12.76',
                            dec: '-55:56:13.9',
                            length: 13.4,
                            nbin: 1024,
                            nchan: 928,
                            tsubint: 8,
                            nant: 53,
                            schedule: '12',
                            phaseup: '12',
                            id: 'Rm9sZFB1bHNhckRldGFpbE5vZGU6OTA3NzY=',
                            images: {
                                edges: [
                                    {
                                        node: {
                                            plotType: 'time',
                                            process: 'raw',
                                            resolution: 'hi',
                                            url: 'phaseVsTime.mock.png'
                                        }
                                    },
                                    {
                                        node: {
                                            plotType: 'profile',
                                            process: 'raw',
                                            resolution: 'hi',
                                            url: 'profile.mock.png'
                                        }
                                    },
                                    {
                                        node: {
                                            plotType: 'phase',
                                            process: 'raw',
                                            resolution: 'hi',
                                            url: 'phaseVsFrequency.mock.png'
                                        }
                                    },

                                ]
                            }
                        }
                    }
                ]
            }
        };

        const { getByAltText } = render(<ObservationTimeView data={data} />);
        expect(getByAltText('Plot profile using raw data.'))
            .toHaveAttribute('src', expect.stringContaining('profile.mock.png'));
        expect(getByAltText('Plot time using raw data.'))
            .toHaveAttribute('src', expect.stringContaining('phaseVsTime.mock.png'));
        expect(
            getByAltText('Plot phase using raw data.'))
            .toHaveAttribute('src', expect.stringContaining('phaseVsFrequency.mock.png')
            );
    });

    it('should render the page with no images available', () => {
        expect.hasAssertions();
        const data = {
            foldObservationDetails: {
                edges: [
                    {
                        node: {
                            beam: 1,
                            utc: '2020-02-04T00:21:21+00:00',
                            proposal: 'SCI-20180516-MB-02',
                            project: 'meertime',
                            frequency: 1283.582031,
                            bw: 775.75,
                            ra: '14:24:12.76',
                            dec: '-55:56:13.9',
                            length: 13.4,
                            nbin: 1024,
                            nchan: 928,
                            tsubint: 8,
                            nant: 53,
                            profileHi: null,
                            phaseVsTimeHi: '',
                            phaseVsFrequencyHi: '',
                            bandpassHi: null,
                            snrVsTimeHi: '',
                            schedule: '12',
                            phaseup: '12',
                            id: 'Rm9sZFB1bHNhckRldGFpbE5vZGU6OTA3NzY=',
                            images: {
                                edges: []
                            }
                        }
                    }
                ]
            }
        };
        render(<ObservationTimeView data={data} />);
        expect(screen.getByText('2020-02-04-00:21:21')).toBeInTheDocument();
    });

});

