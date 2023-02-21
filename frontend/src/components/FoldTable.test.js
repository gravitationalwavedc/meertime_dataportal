import { MockPayloadGenerator, createMockEnvironment } from 'relay-test-utils';
import { QueryRenderer, graphql } from 'react-relay';

import FoldTable from './FoldTable';
import React from 'react';
import { render } from '@testing-library/react';

/* eslint-disable react/display-name */

jest.mock('found/Link',() => ({ children }) => <div>{children}</div>);

describe('the fold table component', () => {
    const environment = createMockEnvironment();
    const TestRenderer = ({ match }) => (
        <QueryRenderer
            environment={environment}
            query={graphql`
            query FoldTableTestQuery @relay_test_operation { 
              ...FoldTable_data
            }
          `}
            render={({ error, props }) => {
                if (props) {
                    return <FoldTable data={props} match={match} router={{}}/>;
                } else if (error) {
                    return error.message;
                }
                return 'Loading...';
            }}
        />
    );
        
    it('displays data from the server', () => {
        expect.hasAssertions();
        const { getAllByText } = render(<TestRenderer match={{ location: { query: {} } }} />);
        environment.mock.resolveMostRecentOperation(operation => MockPayloadGenerator.generate(operation));
        expect(getAllByText('Observations')[0]).toBeInTheDocument();
        expect(getAllByText('42')[0]).toBeInTheDocument();
    });

    it('uses the query parameters in the search form', () => {
        expect.hasAssertions();
        const { getByDisplayValue } = render(
            <TestRenderer
                match={{
                    location:
                        { query: { search: 'J1111-222', project: 'RelBin', mainProject: 'meertime', band: 'L-BAND' } }
                }}
            />
        );
        environment.mock.resolveMostRecentOperation(operation => MockPayloadGenerator.generate(operation));
        expect(getByDisplayValue('J1111-222')).toBeInTheDocument();
        expect(getByDisplayValue('RelBin')).toBeInTheDocument();
        expect(getByDisplayValue('MeerTime')).toBeInTheDocument();
        expect(getByDisplayValue('L-BAND')).toBeInTheDocument();
    });
});
