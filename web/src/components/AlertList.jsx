import React from 'react'
import classnames from 'classnames'

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

const Alerts = ({alerts, onDismiss}) => (
  <div className="row">
    <div className="col-md-8 col-md-offset-2">
      <ul className="list-unstyled">
        {alerts.map((alert) => (
          <li key={alert.id} id={'alert-' + alert.id}>
            <Alert {...alert} onDismiss={() => $('#alert-'+alert.id).fadeOut(100, () => onDismiss(alert.id))}/>
          </li>
        ))
        }
      </ul>
    </div>
  </div>
)

export default Alerts