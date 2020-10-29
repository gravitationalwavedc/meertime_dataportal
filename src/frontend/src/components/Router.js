import React from 'react';
import { BrowserProtocol, queryMiddleware } from 'farce';   
import { createFarceRouter, createRender, makeRouteConfig, Route } from 'found';
import { Resolver } from 'found-relay';
import environment from '../relayEnvironment';
import Fold from '../pages/Fold';
import Login from '../pages/Login';

const routeConfig = () => makeRouteConfig(
    <Route>
        <Route
            path="/"
            Component={Fold}
        />
        <Route
            path="/login"
            Component={Login}
        />
    </Route>
);

const FarceRouter = createFarceRouter({
    historyProtocol: new BrowserProtocol(),
    historyMiddlewares: [queryMiddleware],
    routeConfig: routeConfig(),
    render: createRender({}),
});

const Router = () => <FarceRouter resolver={new Resolver(environment)} />;

export default Router;
