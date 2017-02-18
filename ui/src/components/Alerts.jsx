import React from "react";
import {connect} from "react-redux";
import Snackbar from "material-ui/Snackbar";
import {dismiss} from "../actions/AlertActions";

const Alerts = ({alert, open, onDismiss}) => (
  <Snackbar
    open={open}
    message={alert.text}
    action={"DISMISS"}
    autoHideDuration={5000}
    onActionTouchTap={() => onDismiss(alert.id)}
    onRequestClose={(type) => type !== 'clickaway' && onDismiss(alert.id)}
  />
);

const mapStateToProps = (state) => ({
  alert: state.alerts[0] || {text: ''},
  open: state.alerts.length > 0,
});

const mapDispatchToProps = (dispatch) => ({
  onDismiss: (id) => dispatch(dismiss(id))
});

export default connect(mapStateToProps, mapDispatchToProps)(Alerts);
