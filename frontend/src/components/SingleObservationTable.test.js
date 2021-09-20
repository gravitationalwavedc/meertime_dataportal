import ObservationTimeView from './SingleObservationTable';
import React from 'react';
import { render } from '@testing-library/react';

/* global mockRouter */
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

jest.mock('found/Link',() => ({ children }) => <div>{children}</div>);

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
                            profile: null,
                            phaseVsTime: 'phaseVsTime.mock.png',
                            phaseVsFrequency: 'phaseVsFrequency.mock.png',
                            bandpass: null,
                            snrVsTime: '',
                            schedule: '12',
                            phaseup: '12',
                            id: 'Rm9sZFB1bHNhckRldGFpbE5vZGU6OTA3NzY='
                        }
                    }
                ]
            }
        };

        const { getByAltText } = render(<ObservationTimeView data={data} />);
        expect(getByAltText('profile')).toHaveAttribute('src', expect.stringContaining('image404.png'));
        expect(getByAltText('phaseVsTime')).toHaveAttribute('src', expect.stringContaining('phaseVsTime.mock.png'));
        expect(
            getByAltText('phaseVsFrequency'))
            .toHaveAttribute('src', expect.stringContaining('phaseVsFrequency.mock.png')
            );
        expect(getByAltText('bandpass')).toHaveAttribute('src', expect.stringContaining('image404.png'));
        expect(getByAltText('snrVsTime')).toHaveAttribute('src', expect.stringContaining('image404.png'));
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
                            frequency: 1283.582031,
                            bw: 775.75,
                            ra: '14:24:12.76',
                            dec: '-55:56:13.9',
                            length: 13.4,
                            nbin: 1024,
                            nchan: 928,
                            tsubint: 8,
                            nant: 53,
                            profile: null,
                            phaseVsTime: '',
                            phaseVsFrequency: '',
                            bandpass: null,
                            snrVsTime: '',
                            schedule: '12',
                            phaseup: '12',
                            id: 'Rm9sZFB1bHNhckRldGFpbE5vZGU6OTA3NzY='
                        }
                    }
                ]
            }
        };
        const { getByAltText } = render(<ObservationTimeView data={data} />);
        expect(getByAltText('profile')).toHaveAttribute('src', expect.stringContaining('image404.png'));
        expect(getByAltText('phaseVsTime')).toHaveAttribute('src', expect.stringContaining('image404.png'));
        expect(getByAltText('phaseVsFrequency')).toHaveAttribute('src', expect.stringContaining('image404.png'));
        expect(getByAltText('bandpass')).toHaveAttribute('src', expect.stringContaining('image404.png'));
        expect(getByAltText('snrVsTime')).toHaveAttribute('src', expect.stringContaining('image404.png'));
    });

});
