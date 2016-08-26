import React from 'react'

import Panel from './Panel.jsx'
import SourcesPanelContainer from '../containers/SourcesPanelContainer'
import TagSetPanelContainer from '../containers/TagSetPanelContainer'
import TaggerListContainer from '../containers/TaggerListContainer'
import EvaluatorContainer from '../containers/EvaluatorContainer'

const ToolsPanel = () => (
  <Panel id="panel-element-tools" title="Tools">
    <ul className="nav nav-pills nav-stacked">
      <li className="active"><a data-toggle="pill" href="#tagger">Tagger</a></li>
      <li><a data-toggle="pill" href="#evaluator">Evaluator</a></li>
    </ul>
  </Panel>
);

const Sidebar = () => (
  <div className="panel-group" id="panel-sidebar">
    <ToolsPanel />
    <SourcesPanelContainer />
    <TagSetPanelContainer />
  </div>
);

const TaggerApp = () => (
  <div className="container-fluid">
    <div className="row">
      <aside className="col-sm-3" id="sidebar">
        <Sidebar />
      </aside>
      <div className="col-sm-9 tab-content" id="main">
        <div id="evaluator" className="tab-pane fade">
          <EvaluatorContainer />
        </div>
        <div id="tagger" className="tab-pane fade in active">
          <TaggerListContainer />
        </div>
      </div>
    </div>
  </div>
)

export default TaggerApp