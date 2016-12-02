import React from 'react';
import _ from 'lodash';
import classnames from 'classnames'

import {Icon, SourceIcon, UserLink} from './Source.jsx'


const URL_PATTERN = /(?:(?:http|ftp|https):\/\/)?(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?/gi;

const ToolTip = ({children}) => (
  <a href="#" rel="tooltip" data-container="body" data-toggle="tooltip" data-html="true" data-delay="300"
     title="<div style='padding:0.8rem 0 0.8rem 0;'>
     Confidence<br/>
     <em class='glyphicon glyphicon-certificate' aria-hidden='true'></em>Excellent&nbsp;&nbsp;
     <em class='glyphicon glyphicon-star' aria-hidden='true'></em>Good&nbsp;&nbsp;
     <em class='glyphicon glyphicon-star-empty' aria-hidden='true'></em>Fair
     </div>
     " className="text-danger">
    {children}
  </a>
);

const Tag = ({tag, active, prediction, onToggle}) => {
  if (prediction === undefined || prediction === null) {
    prediction = 3
  }
  // using label buttons to fix focus issues with button
  return (
    <div className="btn-group" role="group">
      <label className={classnames('btn', 'btn-sm', 'ellipsis', {
        'btn-success': prediction < 3,
        'btn-primary': prediction >= 3,
        'active': active
      })}
             type="button" onClick={onToggle}>
        <em className="glyphicon glyphicon-tag" aria-hidden="true"/>{tag}
        {prediction < 3 ?
          <ToolTip>
            <em className={classnames('glyphicon', 'quality', {
              'glyphicon-star-empty': prediction == 2,
              'glyphicon-star': prediction == 1,
              'glyphicon-certificate': prediction == 0
            })}
                aria-hidden="true"/>
          </ToolTip> : null
        }
      </label>
    </div>
  )
};

const UrlText = ({text}) => {
  let matches = text.match(URL_PATTERN);
  if (matches) {
    return (
      <span>
        {_.zip(text.split(URL_PATTERN), matches).map(([frag, url], idx) => {
          return (<span key={idx}>{frag}<span style={{color: "blue"}}>{url}</span></span>);
        })}
      </span>
    );
  } else {
    return <span>{text}</span>
  }
};

const TagList = ({allTags, tags, prediction, onDuplicate, onToggle, onNewTag}) => {
  let input;
  return (
    <form className="form-group" onSubmit={ e => {
      e.preventDefault();
      const newTag = input.value.trim();
      input.value = '';
      if (newTag && newTag != '$$new$$') {
        if (_.includes(allTags, newTag)) {
          onDuplicate(`The entered tag "${newTag}" is a duplicate!`)
        } else {
          onNewTag(newTag)
        }
      }
    }
    }>
      <div className="btn-group btn-group-justified" role="group">

        {_.sortBy(allTags, 1).map((tag, idx) => {
          return <Tag key={idx} tag={tag}
                      active={_.includes(tags, tag)}
                      prediction={prediction[tag]}
                      onToggle={() => onToggle(tag)}/>
        })}

        <div className="btn-group" role="group" key={"$$new$$"}>
          <input type="text" className="form-control new-tag input-sm" placeholder="new tag..."
                 ref={node => input = node}/>
        </div>
      </div>
    </form>
  )
};

const Tagger = ({comment, tagSet, onDuplicate, onToggle, onNewTag}) => {
  const {id, user, source, text, tags, prediction} = comment;
  return (
    <div className="container-fluid tagger">
      <div className="row">

        <Icon id={user.id} type={source.type}/>

        <div className="col-xs-10 fb-main">
          <h4 className="list-group-item-heading">
            <SourceIcon type={source.type}/> <UserLink user={user} type={source.type}/>
          </h4>
          <p className="list-group-item-text" id={'tagger-message-' + id}>
            <UrlText text={text}/>
          </p>
        </div>

        <Icon id={source.slug} type={source.type}/>
      </div>
      <div className="row">
        <TagList allTags={_.union(tags, tagSet)}
                 tags={tags}
                 prediction={prediction}
                 onDuplicate={onDuplicate}
                 onNewTag={(tag) => onNewTag(comment, tag)}
                 onToggle={(tag) => onToggle(comment, tag)}
        />
      </div>
    </div>
  );
};

export default Tagger
