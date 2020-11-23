import { BrowserProtocol, queryMiddleware } from 'farce';
import { Route, createFarceRouter, createRender, makeRouteConfig } from 'found';

import Fold from '../pages/Fold';
import FoldDetail from '../pages/FoldDetail';
import Login from '../pages/Login';
import React from 'react';
import { RedirectException } from 'found';
import { Resolver } from 'found-relay';
import environment from '../relayEnvironment';

const renderPrivateRoute = (Component, props) => {
    if (sessionStorage.getItem('jwt') === null) {
        throw new RedirectException('/login/', 401);
    }
    return <Component {...props}/>;
};


const routeConfig = () => makeRouteConfig(
    <Route>
        <Route
            path="/login/:next?"
            Component={Login}
        />
        <Route
            path="/:jname"
            Component={FoldDetail}
            render={({ Component, props }) => {
                if (sessionStorage.getItem('jwt') === null) {
                    throw new RedirectException('/login/', 401);
                }
                return <Component {...props}/>;
            }}
        />
        <Route
            path="/"
            Component={Fold}
            render={({ Component, props }) => renderPrivateRoute(Component, props)}
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
