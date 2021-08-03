import { MockPayloadGenerator, createMockEnvironment } from 'relay-test-utils';
import { QueryRenderer, graphql } from 'react-relay';

import React from 'react';
import SearchTable from './SearchTable';
import { render } from '@testing-library/react';

/* eslint-disable react/display-name */

jest.mock('found/Link',() => ({ children }) => <div>{children}</div>);

describe('search table component', () => {
    const environment = createMockEnvironment();
    const TestRenderer = () => (
        <QueryRenderer
            environment={environment}
            query={graphql`
            query SearchTableTestQuery @relay_test_operation { 
              ...SearchTable_data
            }
          `}
            render={({ error, props }) => {
                if (props) {
                    return <SearchTable data={props} match={{}} router={{}}/>;
                } else if (error) {
                    return error.message;
                }
                return 'Loading...';
            }}
        />
    );
        
    it('should renders the SearchTable with data', () => {
        expect.hasAssertions();
        const { getAllByText } = render(<TestRenderer />);
        environment.mock.resolveMostRecentOperation(operation => MockPayloadGenerator.generate(operation));
        expect(getAllByText('Observations')[0]).toBeInTheDocument();
        expect(getAllByText('42')[0]).toBeInTheDocument();
    });
});
