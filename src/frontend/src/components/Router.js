import { BrowserProtocol, queryMiddleware } from 'farce';
import { Route, createFarceRouter, createRender, makeRouteConfig } from 'found';

import Fold from '../pages/Fold';
import FoldDetail from '../pages/FoldDetail';
import Login from '../pages/Login';
import React from 'react';
import { RedirectException } from 'found';
import { Resolver } from 'found-relay';
import Search from '../pages/Search';
import SearchmodeDetail from '../pages/SearchmodeDetail';
import Session from '../pages/Session';
import SingleObservation from '../pages/SingleObservation';
import environment from '../relayEnvironment';

const renderPrivateRoute = (Component, props) => {
    if (localStorage.getItem('jwt') === null) {
        throw new RedirectException(`${process.env.REACT_APP_BASE_URL}/login/`, 401);
    }
    return <Component {...props}/>;
};

const routeConfig = () => makeRouteConfig(
    <Route path={process.env.REACT_APP_BASE_URL}>
        <Route
            path="/login/:next?"
            Component={Login}
        />
        <Route
            path="/search/"
            Component={Search}
            render={({ Component, props }) => renderPrivateRoute(Component, props)}
        />
        <Route
            path="/last-session/"
            Component={Session}
            render={({ Component, props }) => renderPrivateRoute(Component, props)}
        />
        <Route
            path="/search/:project/:jname/"
            Component={SearchmodeDetail}
            render={({ Component, props }) => renderPrivateRoute(Component, props)}
        />
        <Route
            path="/fold/:project/:jname/"
            Component={FoldDetail}
            render={({ Component, props }) => renderPrivateRoute(Component, props)}
        />
        <Route
            path="/:jname/:utc/:beam/"
            Component={SingleObservation}
            render={({ Component, props }) => renderPrivateRoute(Component, props)}
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
