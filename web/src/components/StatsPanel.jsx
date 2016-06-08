import React from 'react';
import _ from 'lodash'

import Panel from './Panel.jsx';

const StatsElement = ({source, stats}) => (
  <div className="list-group-item">
    <h2>{source}</h2>
    {_.map(stats, (value, key) => (
      <div key={key}>
        <h3>{key}</h3>
        {_.map(value, (subValue, subKey) => <span key={subKey}>{subKey}: {subValue};&nbsp;</span>)}
      </div>
    ))}
  </div>
)


const StatsPanel = ({sources, stats}) => (
  <Panel id="panel-element-stats" title="Statistics">
    {_.map(stats, (sourceStats, source) => <StatsElement key={source} source={source} stats={sourceStats}/>)}
  </Panel>
)

export default StatsPanel;