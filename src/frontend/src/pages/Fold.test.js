import React from 'react';
import { render } from '@testing-library/react';
import { createMockEnvironment } from 'relay-test-utils';
import Fold from './Fold';

test('renders Fold', () => {
  // Placeholder test to make sure tests are working.
  const environment = createMockEnvironment();
  const { getByLabelText } = render(<Fold environment={environment} />);
  expect(getByLabelText('Select project')).toBeInTheDocument();
});
