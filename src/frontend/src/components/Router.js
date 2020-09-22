import React from 'react';
import { graphql } from 'react-relay';
import { BrowserProtocol, queryMiddleware } from 'farce';   
import { createFarceRouter, createRender, makeRouteConfig, Route, RedirectException } from 'found';
import { Resolver } from 'found-relay';
import environment from '../relayEnvironment';
import Fold from '../pages/Fold';
import Login from '../pages/Login';

const query = graphql`
  query RouterQuery {
    pulsars {
      jname
    }
  }`;

const routeConfig = () => {
  return makeRouteConfig(
    <Route>
      <Route
        path="/"
        Component={Fold}
        query={query}
        render = {({props, error }) => {
          if(error){
            throw new RedirectException('/login', 401);
          };
          return props ? <Fold {...props} /> : <h1>Loading...</h1>;
        }}
      />
      <Route
        path="/login"
        Component={Login}
      />
    </Route>
  );
}

const FarceRouter = createFarceRouter({
  historyProtocol: new BrowserProtocol(),
  historyMiddlewares: [queryMiddleware],
  routeConfig: routeConfig(),
  render: createRender({}),
});

const Router = () => <FarceRouter resolver={new Resolver(environment)} />;

export default Router;
