import React from "react";
import {connect} from "react-redux";

import TimelineControls from "./TimelineControls.jsx";
import Timeline from "./Timeline.jsx";

import {initActivities} from "../../actions/ActivitiesActions";

const separatorBorder = '2px #409db1 solid';

class TimelineFrame extends React.Component {
  componentDidMount() {
    this.props.init();
  }

  render() {
    return (
      <div>
        <TimelineControls/>
        <div style={{borderBottom: separatorBorder}}/>
        <Timeline/>
      </div>
    );
  }
}

const mapStateToProps = (state) => ({});

const mapDispatchToProps = (dispatch) => ({
  init: (force = false) => dispatch(initActivities(force))
});

export default connect(mapStateToProps, mapDispatchToProps)(TimelineFrame);