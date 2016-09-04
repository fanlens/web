import React from 'react'

import AlertListContainer from '../containers/AlertListContainer'


const AlertsApp = ({count}) => (
  <div className="container-fluid">
    <div className="row">
      <div className="col-md-8 col-md-offset-2">
        <AlertListContainer />
      </div>
    </div>
  </div>
);

export default AlertsApp