import React from 'react';
import { MockPayloadGenerator } from 'relay-test-utils';
import { render, fireEvent, waitFor } from '@testing-library/react';
import Login from './Login';
import environment from '../relayEnvironment'; 

/* global router */

describe('login page', () => {
    it('should have a username and password field', () => {
        expect.hasAssertions();
        const { getByLabelText } = render(<Login router={{}} match={{}}/>);
        expect(getByLabelText('Username')).toBeInTheDocument();
        expect(getByLabelText('Password')).toBeInTheDocument();
    });

    it('should submit when there is a username and password', async () => {
        expect.hasAssertions();
        const { getAllByText, getByLabelText } = render(<Login router={router} match={{params: {next: null}}}/>);
        const usernameField = getByLabelText('Username');
        const passwordField = getByLabelText('Password');
        fireEvent.change(usernameField, {target: {value: 'asher'}});
        fireEvent.change(passwordField, {target: {value: 'password'}});
        fireEvent.click(getAllByText('Sign in')[1]);
        const operation = await waitFor(() => environment.mock.getMostRecentOperation());
        environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );
        expect(router.replace).toHaveBeenCalledWith(null);
    });

    it('should have the correct next url', async () => {
        expect.hasAssertions();
        const { getAllByText, getByLabelText } = render(<Login router={router} match={{params: {next: 'search'}}}/>);
        const usernameField = getByLabelText('Username');
        const passwordField = getByLabelText('Password');
        fireEvent.change(usernameField, {target: {value: 'asher'}});
        fireEvent.change(passwordField, {target: {value: 'password'}});
        fireEvent.click(getAllByText('Sign in')[1]);
        const operation = await waitFor(() => environment.mock.getMostRecentOperation());
        environment.mock.resolve(
            operation,
            MockPayloadGenerator.generate(operation)
        );
        expect(router.replace).toHaveBeenCalledWith('search');
    });

    it('should display errors from the server', async () => {
        expect.hasAssertions();
        const { getAllByText, getByLabelText, getByText } = 
          render(<Login router={router} match={{params: {next: null}}}/>);
        const usernameField = getByLabelText('Username');
        const passwordField = getByLabelText('Password');
        fireEvent.change(usernameField, {target: {value: 'asher'}});
        fireEvent.change(passwordField, {target: {value: 'password'}});
        fireEvent.click(getAllByText('Sign in')[1]);
        await waitFor(() => environment.mock.rejectMostRecentOperation(new Error()));
        expect(getByText('Please enter valid credentials.')).toBeInTheDocument();
    });
});
