import { fireEvent, render } from '@testing-library/react';

import ListControls from './ListControls';
import React from 'react';

describe('list controls component', () => {

    it('should handle changes to proposals', () => {
        expect.hasAssertions();
        const handleProposalFilter = jest.fn();
        const { getByLabelText } = render(
            <ListControls
                handleProposalFilter={handleProposalFilter}
                handleBandFilter={jest.fn()}
                searchProps={{ onSearch: jest.fn() }}
                columnToggleProps={{ columns: [] }}
                exportCSVProps={{}}
            />
        );
        fireEvent.change(getByLabelText('Project'), { target: { value: 'TPA' } });
        expect(handleProposalFilter).toHaveBeenCalledWith('TPA');
    });

    it('should handle changes to band', () => {
        expect.hasAssertions();
        const handleBandFilter = jest.fn();
        const { getByLabelText } = render(
            <ListControls
                handleProposalFilter={jest.fn()}
                handleBandFilter={handleBandFilter}
                searchProps={{ onSearch: jest.fn() }}
                columnToggleProps={{ columns: [] }}
                exportCSVProps={{}}
            />
        );
        fireEvent.change(getByLabelText('Band'), { target: { value: 'UHF' } });
        expect(handleBandFilter).toHaveBeenCalledWith('UHF');
    });
});
