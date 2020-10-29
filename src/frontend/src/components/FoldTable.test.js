import React from 'react';
import { render, waitFor } from '@testing-library/react';
import { QueryRenderer, graphql } from 'react-relay';
import { createMockEnvironment, MockPayloadGenerator } from 'relay-test-utils';
import FoldTable from './FoldTable';


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
                    return <FoldTable data={props}/>;
                } else if (error) {
                    return error.message;
                }
                return 'Loading...';
            }}
        />
    );
        
    it('passes', () => {
        expect.hasAssertions();
        const { getByText, getAllByText } = render(<TestRenderer />);
        environment.mock.resolveMostRecentOperation(operation => MockPayloadGenerator.generate(operation));
        expect(getByText('Observations')).toBeInTheDocument();
        expect(getAllByText('42')[0]).toBeInTheDocument();
    });
});
