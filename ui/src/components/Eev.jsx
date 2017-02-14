import React from "react";
import {connect} from "react-redux";
import Paper from "material-ui/Paper";
import ChatInput from "./chat/ChatInput.jsx";
import MessageList from "./chat/MessageList.jsx";
import {initEev} from "../actions/EevActions";
import {initActivities} from "../actions/ActivitiesActions";
import "./Eev.css";

class Eev extends React.Component {
  componentDidMount() {
    this.props.init();
  }

  render() {
    return (
      <main id="eev" style={{display: 'flex', flexDirection: 'column', flex: '1 1 auto', overflow: 'hidden'}}>
        <Paper className="row center-xs"
               style={{zIndex: 1, display: 'flex', flex: '0 0 auto', flexDirection: 'row', backgroundColor: 'white'}}
               rounded={false}
               zDepth={1}>
          <div className="col-md-10 col-xs-12">
            <ChatInput />
          </div>
        </Paper>
        <div className="row center-sm" style={{overflowY: 'scroll'}}>
          <div id="message-list" className="col-sm-8" style={{display: 'flex', flexDirection: 'column'}}>
            <div className="row" style={{display: 'flex', flex: '1 1 auto'}}>
              <div className="col-xs-12">
                <MessageList/>
              </div>
            </div>
          </div>
        </div>
      </main>
    );
  }
}

const mapStateToProps = () => ({});

const mapDispatchToProps = (dispatch) => ({
  init: (force = false) => {
    dispatch(initEev(force));
    dispatch(initActivities(force));
  }
});

export default connect(mapStateToProps, mapDispatchToProps)(Eev);
