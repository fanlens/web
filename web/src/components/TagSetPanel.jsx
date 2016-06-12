import React from 'react';

import Panel, {PanelButton} from './Panel.jsx';

const TagSetElement = ({tagCounts, title, tags}) => (
  <div style={{lineHeight:'1.75em', whiteSpace:'normal'}}>{title}:<br/>
    {tags.map((tag, idx) => (
      <span key={idx} className="badge" style={{border:'2px solid white', marginRight:'0.2em', display:'inline-block'}}>
        <span className="glyphicon glyphicon-tag" aria-hidden="true"></span> {tag} {tagCounts[tag] || ''}
      </span>
    ))}
  </div>
)

const TagSetPanel = ({tagSets, tagCounts, onTagSetSelected}) => (
  <Panel id="panel-element-tagsets" title="Tag Sets">
    {tagSets.map(tagSet => (
      <PanelButton key={tagSet.id} {...tagSet} onClick={() => onTagSetSelected(tagSet.id)}>
        <TagSetElement tagCounts={tagCounts} {...tagSet}/>
      </PanelButton>))}
  </Panel>
)

export default TagSetPanel;