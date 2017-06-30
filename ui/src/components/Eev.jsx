import React from "react";
import {connect} from "react-redux";
import {initActivities} from "../actions/ActivitiesActions";
import TimelineFrame from "./timeline/TimelineFrame.jsx";

class Eev extends React.Component {
  componentDidMount() {
    this.props.init();
  }

  render() {
    return (
      <main id="eev">
        <TimelineFrame/>
      </main>
    );
  }
}

const mapStateToProps = () => ({});

const mapDispatchToProps = (dispatch) => ({
  init: (force = false) => dispatch(initActivities(force))
});

export default connect(mapStateToProps, mapDispatchToProps)(Eev);
