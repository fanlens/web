import React from 'react';
import {connect} from 'react-redux';
import _ from 'lodash';

import RefreshIndicator from 'material-ui/RefreshIndicator';
import Splash from './Splash.jsx';
import {List, ListItem} from 'material-ui/List';

import Message from './Message.jsx';

const Spinner = () => (
  <RefreshIndicator
    size={50}
    left={70}
    top={0}
    loadingColor="#FF9800"
    status="loading"
    style={{
      display: 'inline-block',
      position: 'relative',
      transform: 'translate(10000px, 10000px)' //fix 70px bug
    }}/>
);

const ListItemSpinner = ({loading}) => (
  <ListItem style={loading ? {} : {display: 'none'}}>
    <Spinner />
  </ListItem>
);


const MessageList = ({messages, loading}) => (
  <div>
    {!messages.length ?
      <Splash /> :
      <List className="chat" style={{padding: '16px', backgroundColor: 'white'}}>
        <ListItemSpinner loading={loading} key={-1}/>
        {_.map(messages, (message) => (
          <Message id={message.id} from={message.from.id} meta={message.channelData} key={message.pending || message.id}>
            {message.text}
          </Message>
        ))}
      </List>
    }
  </div>
);

const mapStateToProps = (state) => ({
  messages: _.chain(state.eev.messages).sortBy('id').reverse().value(),
  loading: state.eev.loading
});

export default connect(mapStateToProps)(MessageList);