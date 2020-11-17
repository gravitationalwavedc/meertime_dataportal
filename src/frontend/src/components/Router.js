import React from 'react';
import { BrowserProtocol, queryMiddleware } from 'farce';   
import { createFarceRouter, createRender, makeRouteConfig, Route } from 'found';
import { Resolver } from 'found-relay';
import { RedirectException } from 'found';
import environment from '../relayEnvironment';
import FoldDetail from '../pages/FoldDetail';
import Fold from '../pages/Fold';
import Login from '../pages/Login';

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
