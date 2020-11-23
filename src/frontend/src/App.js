import './assets/scss/theme.scss';

import React from 'react';
import Router from './components/Router';

const App = () => (
    <div className="App h-100" data-testid="mainApp">
        <Router />
    </div>
);

export default App;
