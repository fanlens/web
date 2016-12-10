import React from "react";
import {IndexLink, Link} from "react-router";
import "./Footer.css";

const Footer = () => (
  <footer className="row">
    <div className="col-xs-4 start-xs">
      <ul id="footer-nav">
        <li>
          <Link to="/">Home</Link>
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
      <div className="copyright">Copyright © Fanlens 2017. All Rights Reserved.</div>
    </div>
  </footer>
);

export default Footer;