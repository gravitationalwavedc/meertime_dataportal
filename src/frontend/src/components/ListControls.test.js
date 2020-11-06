import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import ListControls from './ListControls';


describe('list controls component', () => {

    it('should handle changes to proposals', () => {
        expect.hasAssertions();
        const handleProposalFilter = jest.fn();
        const { getByLabelText } = render(
            <ListControls
                handleProposalFilter={handleProposalFilter}
                handleBandFilter={jest.fn()}
                searchProps={{onSearch: jest.fn()}}
            />
        );
        fireEvent.change(getByLabelText('Project'), {target: {value: 'TPA'}});
        expect(handleProposalFilter).toHaveBeenCalledWith('TPA');
    });

    it('should handle changes to band', () => {
        expect.hasAssertions();
        const handleBandFilter = jest.fn();
        const { getByLabelText } = render(
            <ListControls
                handleProposalFilter={jest.fn()}
                handleBandFilter={handleBandFilter}
                searchProps={{onSearch: jest.fn()}}
            />
        );
        fireEvent.change(getByLabelText('Band'), {target: {value: 'UHF'}});
        expect(handleBandFilter).toHaveBeenCalledWith('UHF');
    });
});
