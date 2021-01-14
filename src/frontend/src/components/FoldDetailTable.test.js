import { fireEvent, render, waitFor } from '@testing-library/react';

import FoldDetailTable from './FoldDetailTable';
import React from 'react';

/* eslint-disable react/display-name */

jest.mock('found/Link',() => ({ children }) => <div>{children}</div>);

describe('the fold table component', () => {
    const data = { 
        relayObservationDetails: { 
            jname:'J0255-5304',
            totalObservations:5,
            totalObservationHours:0.3,
            totalProjects:1,
            totalEstimatedDiskSpace:'900.2\u00a0MB',
            totalTimespanDays:291,
            ephemeris: '{"PSRJ":["J1909-3744"],"RAJ":["19:09:47.4346749","1.095e-6"],"DECJ":["-37:44:14.46674","4.538e-5"],"F0":["339.31568728824460432","2.647e-13"],"DM":["10.389056","1.046e-4"],"F1":["-1.6148169107285210e-15","5.198e-21"],"PEPOCH":["54500"],"POSEPOCH":["54500"],"DMEPOCH":["58998.25449720000324305147"],"DM1":["-2.972632617752220e-4","6.024e-6"],"PMRA":["-9.5165787955766117e+0","4.808e-3"],"PMDEC":["-3.5797294377431698e+1","1.688e-2"],"PX":["0.80987819271039196509","2.786e-2"],"SINI":["KIN"],"BINARY":["T2"],"PB":["1.5334494744065780190","1.282e-11"],"T0":["53631.3878301270990220","3.315e-2"],"A1":["1.89799117755602654630","3.137e-8"],"OM":["156.028279496019787910","7.7817"],"ECC":["1.1466363595259235e-7","9.556e-9"],"PBDOT":["5.0346071923954097e-13","5.254e-15"],"M2":["0.20668310617996794669","1.905e-3"],"KOM":["38.5719901001811527330","9.6955"],"KIN":["93.5224409525142085090","8.386e-2"],"EPHVER":["5"],"CLK":["TT(BIPM2013)"],"UNITS":["TCB"],"TIMEEPH":["IF99"],"T2CMETHOD":["IAU2000B"],"CORRECT_TROPOSPHERE":["N"],"EPHEM":["DE421"]}',
            ephemerisUpdatedAt: '2020-05-29T06:33:45+00:00',
            edges:[ 
                { 
                    node:{ 
                        id:'Rm9sZE9ic2VydmF0aW9uRGV0YWlsTm9kZTo4MDE3',
                        utc:'2020-08-03-23:36:45',
                        proposalShort:'TPA',
                        length:1.5,
                        beam:2,
                        bw:544.0,
                        nchan:1024,
                        band:'UHF',
                        nbin:1024,
                        nant:28,
                        nantEff:28,
                        dmFold:15.9,
                        dmPipe:null,
                        rmPipe:null,
                        snrPipe:null,
                        snrSpip:355.2
                    } 
                },
                { 
                    node:{ 
                        id:'Rm9sZE9ic2VydmF0aW9uRGV0YWlsTm9kZTo3MTU0',
                        utc:'2020-07-04-01:10:51',
                        proposalShort:'Relbin',
                        length:1.5,
                        beam:2,
                        bw:856.0, 
                        nchan:1024,
                        band:'L-band',
                        nbin:1024,
                        nant:28,
                        nantEff:28,
                        dmFold:15.9,
                        dmPipe:null,
                        rmPipe:null,
                        snrPipe:null,
                        snrSpip:1923.9 
                    } 
                }
            ] 
        }
    }; 
        
    it('should render data onto the table', () => {
        expect.hasAssertions();
        const { getByText, getAllByText } = render(<FoldDetailTable data={data}/>);
        expect(getByText('Observations')).toBeInTheDocument();
        expect(getByText('Drag to zoom. Click empty area to reset.')).toBeInTheDocument();
        expect(getAllByText('1.5')).toHaveLength(2);
    });

    it('should update the table when the project filter is changed', async () => {
        expect.hasAssertions();
        const { getAllByText, getByLabelText } = render(<FoldDetailTable data={data}/>);
        expect(getAllByText('Relbin')).toHaveLength(2);
        expect(getAllByText('TPA')).toHaveLength(2);
        fireEvent.change(getByLabelText('Project'), { target: { value: 'TPA' } });
        await waitFor(() => {
            // There should only be 1 left as an option in the dropdown.
            expect(getAllByText('Relbin')).toHaveLength(1);
            expect(getAllByText('TPA')).toHaveLength(2);
        });
        fireEvent.change(getByLabelText('Project'), { target: { value: 'All' } });
        await waitFor(() => {
            // There should only be 1 left as an option in the dropdown.
            expect(getAllByText('Relbin')).toHaveLength(2);
            expect(getAllByText('TPA')).toHaveLength(2);
        });
    });
    
    it('should update the table when the band filter is changed', async () => {
        expect.hasAssertions();
        const { getAllByText, getByLabelText } = render(<FoldDetailTable data={data}/>);
        const bandFilter = getByLabelText('Band'); 
        expect(getAllByText('UHF')).toHaveLength(2);
        expect(getAllByText('L-band')).toHaveLength(2);
        fireEvent.change(bandFilter, { target: { value: 'UHF' } });
        await waitFor(() => {
            // There should only be 1 left as an option in the dropdown.
            expect(getAllByText('L-band')).toHaveLength(1);
            expect(getAllByText('UHF')).toHaveLength(2);
        });

        fireEvent.change(bandFilter, { target: { value: 'All' } });
        await waitFor(() => {
            // There should only be 1 left as an option in the dropdown.
            expect(getAllByText('L-band')).toHaveLength(2);
            expect(getAllByText('UHF')).toHaveLength(2);
        });
    });

    it('should disable the view ephemeris button if the data is missing', () => {
        expect.hasAssertions();
        const modifiedData = { relayObservationDetails: { ...data.relayObservationDetails } };
        modifiedData.relayObservationDetails.ephemeris = null;
        const { getByText } = render(<FoldDetailTable data={modifiedData}/>);
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
