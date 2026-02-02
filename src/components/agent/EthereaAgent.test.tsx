import React from 'react';
import { render, screen } from '@testing-library/react';
import EthereaAgent from './EthereaAgent';

test('renders EthereaAgent without crashing', () => {
  render(<EthereaAgent expression="neutral" />);
  // A simple way to check if it rendered is to see if the container is in the document.
  // As the component doesn't have text, we can't use screen.getByText.
  // We will rely on the fact that `render` would throw an error if the component fails to render.
});
