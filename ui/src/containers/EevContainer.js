import {connect} from 'react-redux'

import Eev from '../components/Eev.jsx'
import {sendMessage} from '../actions/EevActions'

const mapStateToProps = (state) => ({
  messages: state.eev.messages,
  ready: state.eev.ws != null
});

const mapDispatchToProps = (dispatch) => ({
  onSend: (text) => dispatch(senMessage(text))
});

const EevContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Eev);

export default EevContainer