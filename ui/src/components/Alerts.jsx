import React from 'react'
import {connect} from 'react-redux'
import classnames from 'classnames'

import {dismiss} from '../actions/AlertActions'
import {AlertActionType} from '../actions/AlertActions'

const ALERT_TITLES = {};
ALERT_TITLES[AlertActionType.ALERT_SUCCESS] = 'Success!';
ALERT_TITLES[AlertActionType.ALERT_INFO] = 'Info!';
ALERT_TITLES[AlertActionType.ALERT_WARNING] = 'Warning!';
ALERT_TITLES[AlertActionType.ALERT_DANGER] = 'Danger!';

const styleForType = (type) => classnames(
  'alert',
  'fade in',
  {
    'alert-success': type == AlertActionType.ALERT_SUCCESS,
    'alert-info': type == AlertActionType.ALERT_INFO,
    'alert-warning': type == AlertActionType.ALERT_WARNING,
    'alert-danger': type == AlertActionType.ALERT_DANGER
  });

const Alert = ({type, text, onDismiss}) => (
  <div className={styleForType(type)}>
    <strong>{ALERT_TITLES[type]}</strong> {text}
    <a href="#" className="close" aria-label="close" onClick={onDismiss}>&times;</a>
  </div>
)

const AlertList = ({alerts, onDismiss}) => (
  <ul className="list-unstyled">
    {alerts.map((alert) => (
      <li key={alert.id} id={'alert-' + alert.id}>
        <Alert {...alert} onDismiss={() => $('#alert-' + alert.id).fadeOut(100, () => onDismiss(alert.id))}/>
      </li>
    ))
    }
  </ul>
);

const mapStateToProps = (state) => {
  return {
    alerts: state.alerts
  }
};

const mapDispatchToProps = (dispatch) => {
  return {
    onDismiss: (id) => {
      dispatch(dismiss(id))
    }
  }
};

const DismissableAlertList = connect(
  mapStateToProps,
  mapDispatchToProps
)(AlertList);

const AlertApp = () => (
  <div className="container-fluid">
    <div className="row">
      <div className="col-md-8 col-md-offset-2">
        <DismissableAlertList />
      </div>
    </div>
  </div>
);

export default AlertApp