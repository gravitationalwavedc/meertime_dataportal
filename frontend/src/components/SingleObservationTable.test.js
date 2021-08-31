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
            'relayObservationModel': {
                'jname': 'J1715-3903',
                'beam': 4,
                'utc': '2020-09-29 17:13:32+00:00',
                'proposal': 'SCI-20180516-MB-02',
                'frequency': 1283.58203125,
                'bw': 856,
                'ra': null,
                'dec': null,
                'length': 299.466701,
                'snrSpip': 38.669903,
                'nbin': 1024,
                'nchan': 1024,
                'tsubint': null,
                'nant': 58,
                'profile': '',
                'phaseVsTime': 'phasevstime.mock.png',
                'phaseVsFrequency': 'phasevsfrequency.mock.png',
                'bandpass': '',
                'snrVsTime': '',
                'schedule': null,
                'phaseup': null
            }
        };
        const { getByAltText } = render(<ObservationTimeView data={data} />);
        expect(getByAltText('profile')).toHaveAttribute('src', expect.stringContaining('image404.png'));
        expect(getByAltText('phaseVsTime')).toHaveAttribute('src', expect.stringContaining('phasevstime.mock.png'));
        expect(
            getByAltText('phaseVsFrequency'))
            .toHaveAttribute('src', expect.stringContaining('phasevsfrequency.mock.png')
            );
        expect(getByAltText('bandpass')).toHaveAttribute('src', expect.stringContaining('image404.png'));
        expect(getByAltText('snrVsTime')).toHaveAttribute('src', expect.stringContaining('image404.png'));
    });

    it('should render the page with no images available', () => {
        expect.hasAssertions();
        const data = {
            'relayObservationModel': {
                'jname': 'J1715-3903',
                'beam': 4,
                'utc': '2020-09-29 17:13:32+00:00',
                'proposal': 'SCI-20180516-MB-02',
                'frequency': 1283.58203125,
                'bw': 856,
                'ra': null,
                'dec': null,
                'length': 299.466701,
                'snrSpip': 38.669903,
                'nbin': 1024,
                'nchan': 1024,
                'tsubint': null,
                'nant': 58,
                'profile': '',
                'phaseVsTime': '',
                'phaseVsFrequency': '',
                'bandpass': '',
                'snrVsTime': '',
                'schedule': null,
                'phaseup': null
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
