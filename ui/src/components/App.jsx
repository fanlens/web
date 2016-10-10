import React from 'react'
import {connect} from 'react-redux'

import Panel from './Panel.jsx'
import SourcesPanelContainer from '../containers/SourcesPanelContainer'
import TagSetPanelContainer from '../containers/TagSetPanelContainer'
import TaggerListContainer from '../containers/TaggerListContainer'
import EevContainer from '../containers/EevContainer'

import {toggle} from '../actions/AppActions'

const ToolsPanel = ({onToggle}) => (
  <Panel id="panel-element-tools" title="Tools">
    <ul className="nav nav-pills nav-stacked">
      <li><a data-toggle="pill" href="#eev" onClick={() => onToggle()}>Talk to eev</a></li>
      <li className="active"><a data-toggle="pill" href="#tagger" onClick={() => onToggle()}>Training Center</a></li>
    </ul>
  </Panel>
);

const Sidebar = ({onToggle}) => (
  <div className="panel-group" id="panel-sidebar">
    <ToolsPanel onToggle={onToggle} />
    <SourcesPanelContainer />
    <TagSetPanelContainer />
  </div>
);

const AppComponent = ({appState, onToggle}) => {
  const {eev, tagger} = appState;
  return (<div className="container-fluid">
      <div className="row">
        <aside className="col-sm-3" id="sidebar">
          <Sidebar onToggle={onToggle} />
        </aside>
        <div className="col-sm-9 tab-content" id="main">
          <div id="eev" className="tab-pane fade in active">
            {eev ? <EevContainer /> : ''}
          </div>
          <div id="tagger" className="tab-pane fade in active">
            {tagger ? <TaggerListContainer /> : ''}
          </div>
        </div>
      </div>
    </div>)
};

const mapStateToProps = (state) => {
  return {
    appState: state.app
  }
};

const mapDispatchToProps = (dispatch) => {
  return {
    onToggle: () => dispatch(toggle())
  }
};

const App = connect(
  mapStateToProps,
  mapDispatchToProps
)(AppComponent);

export default App