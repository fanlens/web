import React from "react";
import {connect} from "react-redux";

import EvaluatorControls from "./EvaluatorControls.jsx";
import Evaluator from "./Evaluator.jsx";

import {initActivities} from "../../actions/ActivitiesActions";

const separatorBorder = '2px #409db1 solid';

class EvaluatorFrame extends React.Component {
  componentDidMount() {
    this.props.init();
  }

  render() {
    return (
      <div>
        <EvaluatorControls/>
        <div style={{borderBottom: separatorBorder}}/>
        <Evaluator/>
      </div>
    );
  }
}

const mapStateToProps = (state) => ({});

const mapDispatchToProps = (dispatch) => ({
  init: (force = false) => dispatch(initActivities(force))
});

export default connect(mapStateToProps, mapDispatchToProps)(EvaluatorFrame);