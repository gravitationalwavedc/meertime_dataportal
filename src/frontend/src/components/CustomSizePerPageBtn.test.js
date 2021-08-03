import { fireEvent, render, waitFor } from '@testing-library/react';

import CustomSizePerPageBtn from './CustomSizePerPageBtn';
import React from 'react';

describe('custome size per page button', () => {

    it('should call the onclick function with correct value', async () => {
        expect.hasAssertions();
        const customClickFunction = jest.fn();
        const { getByText } = render(
            <CustomSizePerPageBtn
                options={[
                    { text: '25', value: 25 },
                    { text: '50', value: 50, page: 50 },
                    { text: '100', value: 100 },
                    { text: '200', value: 200 }
                ]}
                currSizePerPage={200}
                onSizePerPageChange={customClickFunction}
            />);
        let dropdownButton = getByText('200');
        fireEvent.click(dropdownButton);
        await waitFor(() => {
            dropdownButton = getByText('50 per page'); 
        });
        fireEvent.click(dropdownButton);
        expect(customClickFunction).toHaveBeenCalledWith(50);
    });

});
