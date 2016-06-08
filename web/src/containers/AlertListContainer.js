import {connect} from 'react-redux'
import {dismiss} from '../actions/AlertActions'
import AlertList from '../components/AlertList.jsx'

const mapStateToProps = (state) => {
  return {
    alerts: state.alerts
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    onDismiss: (id) => {
      dispatch(dismiss(id))
    }
  }
}

const AlertsContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(AlertList)

export default AlertsContainer