import React from "react";
import Paper from "material-ui/Paper";
import ChatInput from "./chat/ChatInput.jsx";
import MessageList from "./chat/MessageList.jsx";
import "./Eev.css";

const Eev = ({messages}) => (
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


export default Eev;
