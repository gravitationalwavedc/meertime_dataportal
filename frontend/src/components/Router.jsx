import { BrowserProtocol, queryMiddleware } from "farce";
import { Route, createFarceRouter, createRender, makeRouteConfig } from "found";

import AccountActivation from "../pages/AccountActivation";
import Fold from "../pages/Fold";
import FoldDetail from "../pages/FoldDetail";
import TokenManagement from "../pages/TokenManagement";
import Login from "../pages/Login";
import PasswordChange from "../pages/PasswordChange";
import PasswordReset from "../pages/PasswordReset";
import PasswordResetRequest from "../pages/PasswordResetRequest";
import Projects from "../pages/Projects";
import ReactGA from "react-ga";
import { RedirectException } from "found";
import Register from "../pages/Register";
import RegisterVerify from "../pages/RegisterVerify";
import { Resolver } from "found-relay";
import Search from "../pages/Search";
import SearchDetail from "../pages/SearchDetail";
import Session from "../pages/Session";
import SessionList from "../pages/SessionList";
import SingleObservation from "../pages/SingleObservation";
import LoadingState from "../components/LoadingState";
import environment from "../relayEnvironment";
import { Suspense } from "react";

//Initialise Google Analytics
const trackingID = "UA-217876641-1";

ReactGA.initialize(trackingID, { testMode: import.meta.env.DEV });

ReactGA.set({
  username: localStorage.getItem("username"),
});

const renderTrackingRoute = (Component, props) => {
  ReactGA.pageview(props.match.location.pathname);
  return (
    <Suspense fallback={<LoadingState />}>
      <Component {...props} />
    </Suspense>
  );
};

const renderPrivateRoute = (Component, props) => {
  if (localStorage.getItem("username") === null) {
    // There will always be a redirect route.
    const redirectRoute = props.match.location.pathname;

    if (redirectRoute === "/") {
      throw new RedirectException("/login", 401);
    }

    const redirectPath = `/login?next=${redirectRoute}`;
    throw new RedirectException(redirectPath, 401);
  }
  // Send data to google analytics
  return renderTrackingRoute(Component, props);
};

const routeConfig = () =>
  makeRouteConfig(
    <Route>
      <Route
        path="/login/"
        Component={Login}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/activate/:code/"
        Component={AccountActivation}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/register/"
        Component={Register}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/password_reset/"
        Component={PasswordReset}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/password_reset_request/"
        Component={PasswordResetRequest}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/verify/:code/"
        Component={RegisterVerify}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/search/"
        Component={Search}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/search/:mainProject/:jname/"
        Component={SearchDetail}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/last-session/"
        Component={Session}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/session/:id/"
        Component={Session}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/sessions/"
        Component={SessionList}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/fold/:mainProject/:jname/"
        Component={FoldDetail}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/:mainProject/:jname/:utc/:beam/"
        Component={SingleObservation}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
      />
      <Route
        path="/projects/"
        Component={Projects}
        render={({ Component, props }) => renderPrivateRoute(Component, props)}
      />
      <Route
        path="/password_change/"
        Component={PasswordChange}
        render={({ Component, props }) => renderPrivateRoute(Component, props)}
      />
      <Route
        path="/api-tokens/"
        Component={TokenManagement}
        render={({ Component, props }) => renderPrivateRoute(Component, props)}
      />
      <Route
        path="/"
        Component={Fold}
        render={({ Component, props }) => renderTrackingRoute(Component, props)}
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
