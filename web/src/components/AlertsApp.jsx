import React from 'react'

import AlertListContainer from '../containers/AlertListContainer'


const TaggerApp = ({count}) => (
  <div className="container-fluid" id="alerts">
    <AlertListContainer />
  </div>
)

export default TaggerApp