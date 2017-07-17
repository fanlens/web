import React from "react";
import {Link} from "react-router-dom";
import Paper from "material-ui/Paper";
import "./Footer.css";

const Footer = () => (
  <footer>
    <Paper className="row" zDepth={1} style={{height: '100%', width: '100%', margin: 0, padding: '0.25em'}} rounded={false}>
      <div className="col-xs-4 start-xs">
        <ul id="footer-nav">
          <li>
            <a href="/">Home</a>
          </li>
          <li>
            <a href="/v4/ui">App</a>
          </li>
          <li>
            <Link to="/team">Team</Link>
          </li>
          <li>
            <Link to="/legal">Legal</Link>
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