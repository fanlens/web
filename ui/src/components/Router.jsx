import React from "react";
import {BrowserRouter, Route, Switch} from "react-router-dom";
import NotFound from "./NotFound.jsx";
import EvaluatorFrame from "./evaluator/EvaluatorFrame.jsx";
import TimelineFrame from "./timeline/TimelineFrame.jsx";
import Team from "./Team.jsx";
import Legal from "./Legal.jsx";
import Enterprise from "./enterprise/Enterprise.jsx";
import MuiThemeProvider from "material-ui/styles/MuiThemeProvider";
import Footer from "./Footer.jsx";
import Sidebar from "./sidebar/Sidebar.jsx";
import Alerts from "./Alerts.jsx";
import Skype from "./skype/Skype.jsx";

const App = () => (
  <MuiThemeProvider>
    <div>
      <Sidebar/>
      <Switch>
        <Route exact path='/v3/ui/' component={TimelineFrame}/>
        <Route path='/v3/ui/timeline' component={TimelineFrame}/>
        <Route path='/v3/ui/evaluator' component={EvaluatorFrame}/>
        <Route path='/v3/ui/team' component={Team}/>
        <Route path='/v3/ui/legal' component={Legal}/>
        <Route path='/v3/ui/enterprise' component={Enterprise}/>
        <Route path='/v3/ui/' component={NotFound}/>
      </Switch>
      <Skype/>
      <Footer/>
      <Alerts/>
    </div>
  </MuiThemeProvider>
);

const AppRouter = () => (
  <BrowserRouter>
    <App/>
  </BrowserRouter>
);

export default AppRouter;