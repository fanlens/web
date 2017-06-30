import React from "react";
import {connect} from "react-redux";
import {setInputActive} from "../../actions/AppActions";
import "./Splash.css";

const Splash = ({onActivate}) => (
  <div>
    <div
      className="intro-message"
      onClick={onActivate}>
      <div className="title">
        <h1>
          <img src="/cdn/img/logo.png"/><em>f</em>anlens</h1>
        <h3>Artificial Intelligence<br/>
          Social Media Management</h3>
      </div>
    </div>
  </div>
);

const mapDispatchToProps = (dispatch) => ({
  onActivate: () => {
    dispatch(setInputActive(true));
    document.getElementById('guiframeworkssucksometimes').focus();
  }
});

export default connect((state) => ({}), mapDispatchToProps)(Splash);

