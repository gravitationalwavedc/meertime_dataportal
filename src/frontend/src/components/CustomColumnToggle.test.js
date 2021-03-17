import { fireEvent, render, waitFor } from '@testing-library/react';

import CustomColumnToggle from './CustomColumnToggle';
import React from 'react';

describe('custom toggle button', () => {

    const columns = [
        { dataField: 'jname', text: 'JName', align: 'center', headerAlign: 'center', sort:true },
        { dataField: 'last', text: 'Last', sort: true },
        { dataField: 'first', text: 'First', sort: true },
        { dataField: 'proposalShort', text: 'Project', sort: true },
        { dataField: 'timespan', text: 'Timespan', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'nobs', text: 'Observations', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'totalTintH', text: 'Total int [h]', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'avgSnr5min', text: 'Avg S/N pipe (5 mins)', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'maxSnr5min', text: 'Max S/N pipe (5 mins)', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'latestSnr', text: 'Last S/N raw', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'latestTintM', text: 'Last int. [m]', align: 'right', headerAlign: 'right', sort: true },
        { dataField: 'action', text: '', align: 'center', headerAlign: 'center', sort: false }
    ];

    let toggles = { jname: true, last: true, first: true };

    it('should display a dropdown when clicked', async () => {
        expect.hasAssertions();
        const { getByText, queryByText, getByTestId } = render(
            <CustomColumnToggle 
                columns={columns} 
                onColumnToggle={{}} 
                toggles={{}} 
                exportCSVProps={{}} />
        );
        await waitFor(() => {
            expect(queryByText('jname')).not.toBeInTheDocument();
        });
        fireEvent.click(getByTestId('tableOptions')); 
        await waitFor(() => {
            expect(getByText('JName')).toBeInTheDocument();
        });
    });

    it('should show which columns are active', () => {
        expect.hasAssertions();
        const { rerender, getByText, getByTestId, getAllByTestId } = render(
            <CustomColumnToggle 
                columns={columns} 
                onColumnToggle={(dataField) => {
                    toggles[dataField] = !toggles[dataField];
                }}
                toggles={toggles} 
                exportCSVProps={{}} />
        );
        fireEvent.click(getByTestId('tableOptions')); 
        const preToggleCount = getAllByTestId('itemChecked').length;
        fireEvent.click(getByText('JName'));
        rerender(
            <CustomColumnToggle 
                columns={columns} 
                onColumnToggle={{}}
                toggles={toggles} 
                exportCSVProps={{}} />
        );
        const postToggleCount = getAllByTestId('itemChecked').length;
        expect(postToggleCount).toBeLessThan(preToggleCount);
    });
});
