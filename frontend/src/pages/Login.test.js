import { fireEvent, render, waitFor } from '@testing-library/react';

import Login from './Login';
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

describe('login page', () => {
    it('should have a username and password field', () => {
        expect.hasAssertions();
        const { getByLabelText } = render(<Login router={{}} match={{}}/>);
        expect(getByLabelText('Email')).toBeInTheDocument();
        expect(getByLabelText('Password')).toBeInTheDocument();
    });

    it('should submit when there is a username and password', async () => {
        expect.hasAssertions();
        const { getAllByText, getByLabelText } = render(<Login router={mockRouter} match={{ params: { next: null } }}/>);
        const usernameField = getByLabelText('Email');
        const passwordField = getByLabelText('Password');
        fireEvent.change(usernameField, { target: { value: 'asher' } });
        fireEvent.change(passwordField, { target: { value: 'password' } });
        fireEvent.click(getAllByText('Sign in')[1]);
        const operation = await waitFor(() => environment.mock.getMostRecentOperation());
        environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );
        expect(mockRouter.replace).toHaveBeenCalledWith('/null/');
    });

    it('should have the correct next url', async () => {
        expect.hasAssertions();
        const { getAllByText, getByLabelText } = render(
            <Login router={mockRouter} match={{ params: { next: 'search' } }}/>
        );
        const usernameField = getByLabelText('Email');
        const passwordField = getByLabelText('Password');
        fireEvent.change(usernameField, { target: { value: 'asher' } });
        fireEvent.change(passwordField, { target: { value: 'password' } });
        fireEvent.click(getAllByText('Sign in')[1]);
        const operation = await waitFor(() => environment.mock.getMostRecentOperation());
        environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );
        expect(mockRouter.replace).toHaveBeenCalledWith('/search/');
    });

    it('should display errors from the server', async () => {
        expect.hasAssertions();
        const { getAllByText, getByLabelText, getByText } = 
          render(<Login router={mockRouter} match={{ params: { next: null } }}/>);
        const usernameField = getByLabelText('Email');
        const passwordField = getByLabelText('Password');
        fireEvent.change(usernameField, { target: { value: 'asher' } });
        fireEvent.change(passwordField, { target: { value: 'password' } });
        fireEvent.click(getAllByText('Sign in')[1]);
        await waitFor(() => environment.mock.rejectMostRecentOperation(new Error()));
        expect(getByText('Please enter valid credentials.')).toBeInTheDocument();
    });
});
