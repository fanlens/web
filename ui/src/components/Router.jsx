import React from "react";
import {Router, Route, IndexRoute, browserHistory, DefaultRoute} from "react-router";
import App from "./App.jsx";
import NotFound from "./NotFound.jsx";
import Eev from "./Eev.jsx";
import Team from "./Team.jsx";
import Legal from "./Legal.jsx";
import Dashboard from "./Dashboard.jsx";
import Enterprise from "./enterprise/Enterprise.jsx";

const AppRouter = () => (
  <Router history={browserHistory}>
    <Route path='/v3/ui/' component={App}>
      <IndexRoute component={Eev}/>
      <Route path='team' component={Team}/>
      <Route path='legal' component={Legal}/>
      <Route path='dashboard' component={Dashboard}/>
      <Route path='enterprise' component={Enterprise}/>
      <Route path='*' component={NotFound}/>
    </Route>
  </Router>
);

export default AppRouter;