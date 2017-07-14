import React from "react";
import {NavLink} from "react-router-dom";
import Paper from "material-ui/Paper";
import "./Footer.css";

const Footer = () => (
  <footer>
    <Paper className="row" zDepth={1} style={{height: '100%', width: '100%', margin: 0, padding: '0.25em'}} rounded={false}>
      <div className="col-xs-4 start-xs">
        <ul id="footer-nav">
          <li>
            <NavLink to="/v3/ui/">Home</NavLink>
          </li>
          <li>
            <NavLink to="/v3/ui/team">Team</NavLink>
          </li>
          <li>
            <NavLink to="/v3/ui/legal">Legal</NavLink>
          </li>
        </ul>
      </div>
      <div className="col-xs end-xs">
        <div className="copyright">© Fanlens 2017. All Rights Reserved.</div>
      </div>
    </Paper>
  </footer>
);

export default Footer;