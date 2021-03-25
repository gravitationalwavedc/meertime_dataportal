import './assets/scss/theme.scss';

import React from 'react';
import Router from './components/Router';
import { ScreenSizeProvider } from './context/screenSize-context';

const App = () => (
    <ScreenSizeProvider>
        <div className="App h-100" data-testid="mainApp">
            <Router />
        </div>
    </ScreenSizeProvider>
);

export default App;
