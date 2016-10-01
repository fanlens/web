import {connect} from 'react-redux'

import Eev from '../components/Eev.jsx'
import {initEev, sendChatbotMessage, enter, exit} from '../actions/EevActions'

const mapStateToProps = (state) => {
  return {
    messages: state.eev.messages,
    ready: state.eev.conversation.token != null
  }
};

const mapDispatchToProps = (dispatch) => {
  return {
    onInit: () => dispatch(initEev()),
    onSend: (text) => dispatch(sendChatbotMessage(text)),
    onEnter: () => dispatch(enter()),
    onExit: () => dispatch(exit()),
  }
};

const EevContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Eev);

export default EevContainer