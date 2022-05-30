import { fireEvent, render, waitFor } from '@testing-library/react';

import FoldDetailTable from './FoldDetailTable';
import React from 'react';

/* eslint-disable react/display-name,  max-len */
jest.mock('found/Link',() => ({ children }) => <div>{children}</div>);

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

describe('the fold table component', () => {
    const data = {
        foldObservationDetails: {
            totalObservations: 4,
            totalObservationHours: 0,
            totalProjects: 1,
            totalEstimatedDiskSpace: '26.5 MB',
            totalTimespanDays: 53,
            maxPlotLength: 360,
            minPlotLength: 0,
            edges: [
                {
                    node: {
                        id: 'Rm9sZFB1bHNhckRldGFpbE5vZGU6OTA3NzY=',
                        utc: '2020-02-04T00:21:21+00:00',
                        project: 'Relbin',
                        ephemeris: '{"DM": {"err": "2.0000", "val": "198.7"}, "F0": {"err": "3.000e-11", "val": "1.29806938188"}, "F1": {"err": "4.000e-18", "val": "-1.3150000000000000e-15"}, "RAJ": {"err": "3.000e-2", "val": "14:24:12.76"}, "DECJ": {"err": "0.3000", "val": "-55:56:13.9"}, "PSRJ": {"val": "J1424-5556"}, "UNITS": {"val": "TDB"}, "EPHVER": {"val": "5"}, "PEPOCH": {"val": "52260.00000000000000000000"}, "T2CMETHOD": {"val": "TEMPO"}, "CORRECT_TROPOSPHERE": {"val": "N"}}',
                        ephemerisIsUpdatedAt: '2020-12-15T11:19:22+00:00',
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
                        flux: 12
                    }
                },
                {
                    node: {
                        id: 'Rm9sZFB1bHNhckRldGFpbE5vZGU6MTA0MjQ2',
                        utc: '2020-01-08T10:38:34+00:00',
                        project: 'Relbin',
                        ephemeris: '{"DM": {"err": "2.0000", "val": "198.7"}, "F0": {"err": "3.000e-11", "val": "1.29806938188"}, "F1": {"err": "4.000e-18", "val": "-1.3150000000000000e-15"}, "RAJ": {"err": "3.000e-2", "val": "14:24:12.76"}, "DECJ": {"err": "0.3000", "val": "-55:56:13.9"}, "PSRJ": {"val": "J1424-5556"}, "UNITS": {"val": "TDB"}, "EPHVER": {"val": "5"}, "PEPOCH": {"val": "52260.00000000000000000000"}, "T2CMETHOD": {"val": "TEMPO"}, "CORRECT_TROPOSPHERE": {"val": "N"}}',
                        ephemerisIsUpdatedAt: '2021-05-24T13:44:39+00:00',
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
                        snBackend: 66.6,
                        snMeerpipe: null,
                        flux: 1.2
                    }
                },
                {
                    node: {
                        id: 'Rm9sZFB1bHNhckRldGFpbE5vZGU6MTA0MjQ3',
                        utc: '2020-02-14T03:21:11+00:00',
                        project: 'TPA',
                        ephemeris: '{"DM": {"err": "2.0000", "val": "198.7"}, "F0": {"err": "3.000e-11", "val": "1.29806938188"}, "F1": {"err": "4.000e-18", "val": "-1.3150000000000000e-15"}, "RAJ": {"err": "3.000e-2", "val": "14:24:12.76"}, "DECJ": {"err": "0.3000", "val": "-55:56:13.9"}, "PSRJ": {"val": "J1424-5556"}, "UNITS": {"val": "TDB"}, "EPHVER": {"val": "5"}, "PEPOCH": {"val": "52260.00000000000000000000"}, "T2CMETHOD": {"val": "TEMPO"}, "CORRECT_TROPOSPHERE": {"val": "N"}}',
                        ephemerisIsUpdatedAt: '2021-05-24T13:44:39+00:00',
                        length: 13.3,
                        beam: 1,
                        bw: 856,
                        nchan: 1024,
                        band: 'L-Band',
                        nbin: 1024,
                        nant: 60,
                        nantEff: 62,
                        dmFold: -1,
                        dmMeerpipe: null,
                        rmMeerpipe: null,
                        snBackend: 83.3,
                        snMeerpipe: null,
                        flux: 3.4
                    }
                },
                {
                    node: {
                        id: 'Rm9sZFB1bHNhckRldGFpbE5vZGU6MTA0MjQ4',
                        utc: '2020-03-01T04:51:19+00:00',
                        project: 'TPA',
                        ephemeris: '{"DM": {"err": "2.0000", "val": "198.7"}, "F0": {"err": "3.000e-11", "val": "1.29806938188"}, "F1": {"err": "4.000e-18", "val": "-1.3150000000000000e-15"}, "RAJ": {"err": "3.000e-2", "val": "14:24:12.76"}, "DECJ": {"err": "0.3000", "val": "-55:56:13.9"}, "PSRJ": {"val": "J1424-5556"}, "UNITS": {"val": "TDB"}, "EPHVER": {"val": "5"}, "PEPOCH": {"val": "52260.00000000000000000000"}, "T2CMETHOD": {"val": "TEMPO"}, "CORRECT_TROPOSPHERE": {"val": "N"}}',
                        ephemerisIsUpdatedAt: '2021-05-24T13:44:39+00:00',
                        length: 5.3,
                        beam: 2,
                        bw: 856,
                        nchan: 1024,
                        band: 'L-Band',
                        nbin: 1024,
                        nant: 29,
                        nantEff: 29,
                        dmFold: -1,
                        dmMeerpipe: null,
                        rmMeerpipe: null,
                        snBackend: 38.4,
                        snMeerpipe: null,
                        flux: null
                    }
                }
            ]
        }
    }; 
        
    const dataNoEphemeris = { 
        'foldObservationDetails': {
            'totalObservations': 4,
            'totalObservationHours': 0,
            'totalProjects': 1,
            'totalEstimatedDiskSpace': '26.5 MB',
            'totalTimespanDays': 53,
            'maxPlotLength': 360,
            'minPlotLength': 0,
            'edges': [
                {
                    'node': {
                        'id': 'Rm9sZFB1bHNhckRldGFpbE5vZGU6OTA3NzY=',
                        'utc': '2020-02-04T00:21:21+00:00',
                        'project': 'TPA',
                        'ephemeris': null,
                        'ephemerisIsUpdatedAt': '2020-12-15T11:19:22+00:00',
                        'length': 13.4,
                        'beam': 1,
                        'bw': 775.75,
                        'nchan': 928,
                        'band': 'L-Band',
                        'nbin': 1024,
                        'nant': 53,
                        'nantEff': 53,
                        'dmFold': -1,
                        'dmMeerpipe': null,
                        'rmMeerpipe': null,
                        'snBackend': 134.5,
                        'snMeerpipe': null,
                        'flux': null
                    }
                },
            ]
        }
    }; 

    it('should render data onto the table', () => {
        expect.hasAssertions();
        const { getByText, getAllByText } = render(<FoldDetailTable data={data} />);
        expect(getByText('Observations')).toBeInTheDocument();
        expect(getByText('Drag to zoom, click empty area to reset, double click to view utc.')).toBeInTheDocument();
        expect(getAllByText('2')).toHaveLength(2);
    });

    it('should update the table when the band filter is changed', async () => {
        expect.hasAssertions();
        const { queryByText, getAllByText, getByLabelText } = render(<FoldDetailTable data={data} jname='J123-123'/>);
        const bandFilter = getByLabelText('Band'); 
        expect(getAllByText('UHF')).toHaveLength(3);
        expect(getAllByText('L-Band')).toHaveLength(2);

        fireEvent.change(bandFilter, { target: { value: 'UHF' } });
        expect(queryByText('L-Band')).not.toBeInTheDocument();

        fireEvent.change(bandFilter, { target: { value: 'All' } });
        await waitFor(() => {
            // There should only be 1 left as an option in the dropdown.
            expect(getAllByText('L-Band')).toHaveLength(2);
            expect(getAllByText('UHF')).toHaveLength(3);
        });
    });

    it('should disable the view ephemeris button if the data is missing', () => {
        expect.hasAssertions();
        const { getByText } = render(<FoldDetailTable data={dataNoEphemeris}/>);
        expect(getByText('Folding ephemeris unavailable')).toBeDisabled();
    });

    it('should toggle the ephemeris modal', () => {
        expect.hasAssertions();
        const { getByText , queryByRole } = render(<FoldDetailTable data={data}/>);
        const toggleEphemerisButton = getByText('View folding ephemeris');
        expect(queryByRole('dialog')).not.toBeInTheDocument();
        fireEvent.click(toggleEphemerisButton);
        expect(queryByRole('dialog')).toBeInTheDocument();
    });
});
