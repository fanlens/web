import React from 'react'

import SourcesPanelContainer from '../containers/SourcesPanelContainer'
import TagSetPanelContainer from '../containers/TagSetPanelContainer'
import StatsPanelContainer from '../containers/StatsPanelContainer'
import TaggerListContainer from '../containers/TaggerListContainer'

const Sidebar = () => (
  <div className="panel-group" id="panel-sidebar">
    <SourcesPanelContainer />
    <TagSetPanelContainer />
  </div>
);

const InfoBar = () => (
  <div className="panel-group" id="panel-sidebar">
    <StatsPanelContainer />
  </div>
)

const TaggerApp = ({count}) => (
  <div className="container-fluid">
    <div className="row">
      <aside className="col-sm-2" id="sidebar">
        <Sidebar />
      </aside>
      <main className="col-sm-7" id="main">
        <TaggerListContainer count={count}/>
      </main>
      <aside className="col-sm-3" id="infobar">
        <InfoBar />
      </aside>
    </div>
  </div>
)

export default TaggerApp