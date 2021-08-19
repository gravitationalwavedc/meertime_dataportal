import JobCardsList from './JobCardsList';
import React from 'react';
import { render } from '@testing-library/react';

/* eslint-disable react/display-name */

jest.mock('found/Link',() => ({ children }) => <div>{children}</div>);

describe('card list component', () => {
    const data = [
        {
            avgSnr5min: 1519.2,
            first: '2019-10-18T23:29:57+00:00',
            id: 'Rm9sZE9ic2VydmF0aW9uTm9kZTo1NzM=',
            jname: 'J0255-5304',
            last: '2020-08-03T23:36:45+00:00',
            latestSnr: 355.2,
            latestTintM: 1.5,
            maxSnr5min: 1519.2,
            nobs: 5,
            proposalShort: 'TPA',
            timespan: '290',
            totalTintH: 0.3
        },
        { 
            avgSnr5min: 377.8,
            first: '2019-10-18T22:50:26+00:00',
            id: 'Rm9sZE9ic2VydmF0aW9uTm9kZTo1NzE=',
            jname: 'J0152-1637',
            last: '2020-08-03T23:33:18+00:00',
            latestSnr: 3462.2,
            latestTintM: 2.8,
            maxSnr5min: 377.8,
            nobs: 4,
            proposalShort: 'TPA',
            timespan: '290',
            totalTintH: 0.6 
        },
        {
            avgSnr5min: 66.9,
            first: '2019-11-12T20:49:38+00:00',
            id: 'Rm9sZE9ic2VydmF0aW9uTm9kZTo3Njc=',
            jname: 'J0151-0635',
            last: '2020-08-03T23:27:50+00:00',
            latestSnr: 700.7,
            latestTintM: 5.2,
            maxSnr5min: 66.9,
            nobs: 4,
            proposalShort: 'TPA',
            timespan: '265',
            totalTintH: 1
        }
    ];

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

    it('should display data without a search term', () => {
        expect.hasAssertions();
        const { getByText } = render(<JobCardsList data={data} columns={columns} search={{ searchText: '' }} />);
        expect(getByText('J0151-0635')).toBeInTheDocument();
    });

    it('should filter display data based on the search term', () => {
        expect.hasAssertions();
        const { getByText, queryByText } = render(
            <JobCardsList data={data} columns={columns} search={{ searchText: 'J0255' }} />
        );
        expect(queryByText('J0151-0635')).not.toBeInTheDocument();
        expect(getByText('J0255-5304')).toBeInTheDocument();
    });

    it('should ignore columns that are not searchable', () => {
        expect.hasAssertions();
        columns[0]['searchable'] = false;
        const { queryByText } = render(
            <JobCardsList data={data} columns={columns} search={{ searchText: 'J0255' }} />
        );
        expect(queryByText('J0255-5304')).not.toBeInTheDocument();

    });
});

