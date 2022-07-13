import { fireEvent, render, waitFor } from '@testing-library/react';

import PasswordResetRequest from './PasswordResetRequest';
import { MockPayloadGenerator } from 'relay-test-utils';
import React from 'react';
import environment from '../relayEnvironment';

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

describe('password reset request page', () => {
    it('should have an email field', () => {
        expect.hasAssertions();
        const { getByLabelText } = render(<PasswordResetRequest router={{}} match={{}}/>);
        expect(getByLabelText('Email')).toBeInTheDocument();
    });

    it('should display errors from the server', async () => {
        expect.hasAssertions();
        const { getAllByText, getByLabelText, getByText } =
          render(<PasswordResetRequest router={mockRouter} match={{ params: { next: null } }}/>);
        const emailField = getByLabelText('Email');
        fireEvent.change(emailField, { target: { value: 'e@mail.com' } });
        fireEvent.click(getAllByText('Password Reset Request')[1]);
        await waitFor(() => environment.mock.rejectMostRecentOperation(new Error()));
        expect(getByText('Something went wrong, please try later.')).toBeInTheDocument();
    });
});
