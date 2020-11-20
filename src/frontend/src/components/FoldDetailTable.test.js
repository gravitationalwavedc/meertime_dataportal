import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import FoldDetailTable from './FoldDetailTable';

/* eslint-disable react/display-name */

jest.mock('found/Link',() => ({ children }) => <div>{children}</div>);

describe('the fold table component', () => {
    const data = { 
        foldObservationDetails: { 
            jname:'J0255-5304',
            totalObservations:5,
            totalObservationHours:0.3,
            totalProjects:1,
            totalEstimatedDiskSpace:'900.2\u00a0MB',
            totalTimespanDays:291,
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
});
