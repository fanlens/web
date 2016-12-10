import React from "react";
import {Router, Route, IndexRoute, browserHistory, DefaultRoute} from "react-router";
import MuiThemeProvider from "material-ui/styles/MuiThemeProvider";
import NotFound from "./NotFound.jsx";
import Eev from "./Eev.jsx";
import Team from "./Team.jsx";
import Legal from "./Legal.jsx";
import Footer from "./Footer.jsx";
import Sidebar from "./sidebar/Sidebar.jsx";

const AppContainer = ({children}) => (
  <MuiThemeProvider>
    <div style={{display: 'flex', flexDirection: 'column', height: '100%'}}>
      <Sidebar/>
      {children}
      <Footer/>
    </div>
  </MuiThemeProvider>
);

const App = () => (
  <Router history={browserHistory}>
    <Route path='/' component={AppContainer}>
      <IndexRoute component={Eev}/>
      <Route path='team' component={Team}/>
      <Route path='legal' component={Legal}/>
      <Route path='*' component={NotFound}/>
    </Route>
  </Router>
);


export default App;