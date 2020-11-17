import React from 'react';
import { render } from '@testing-library/react';
import { QueryRenderer, graphql } from 'react-relay';
import { createMockEnvironment, MockPayloadGenerator } from 'relay-test-utils';
import FoldTable from './FoldTable';

/* eslint-disable react/display-name */

jest.mock('found/Link',() => ({ children }) => <div>{children}</div>);

describe('the fold table component', () => {
    const environment = createMockEnvironment();
    const TestRenderer = () => (
        <QueryRenderer
            environment={environment}
            query={graphql`
            query FoldTableTestQuery @relay_test_operation { 
              ...FoldTable_data
            }
          `}
            render={({ error, props }) => {
                if (props) {
                    return <FoldTable data={props} match={{}} router={{}}/>;
                } else if (error) {
                    return error.message;
                }
                return 'Loading...';
            }}
        />
    );
        
    it('passes', () => {
        expect.hasAssertions();
        const { getAllByText } = render(<TestRenderer />);
        environment.mock.resolveMostRecentOperation(operation => MockPayloadGenerator.generate(operation));
        expect(getAllByText('Observations')[0]).toBeInTheDocument();
        expect(getAllByText('42')[0]).toBeInTheDocument();
    });
});
