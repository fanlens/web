import React from "react";
import {connect} from "react-redux";

import TimelineControls from "./TimelineControls.jsx";
import Timeline from "./Timeline.jsx";

const separatorBorder = '2px #409db1 solid';
const TimelineFrame = () => (
  <div>
    <TimelineControls/>
    <div style={{borderBottom: separatorBorder}}/>
    <div style={{overflow: 'scroll'}}>
    <Timeline/>
    </div>
  </div>
);

const mapStateToProps = (state) => ({});

const mapDispatchToProps = (dispatch) => ({});

export default connect(mapStateToProps, mapDispatchToProps)(TimelineFrame);