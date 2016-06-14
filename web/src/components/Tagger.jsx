import React from 'react';
import _ from 'lodash';
import classnames from 'classnames'


const URL_PATTERN = /(?:(?:http|ftp|https):\/\/)?(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?/gi;

const ToolTip = ({children}) => (
  <a href="#" rel="tooltip" data-container="body" data-toggle="tooltip" data-html="true" data-delay="300"
     title="<div style='padding:0.8rem 0 0.8rem 0;'>
     Confidence<br/>
     <em class='glyphicon glyphicon-certificate' aria-hidden='true'></em>Excellent&nbsp;&nbsp;
     <em class='glyphicon glyphicon-star' aria-hidden='true'></em>Good&nbsp;&nbsp;
     <em class='glyphicon glyphicon-star-empty' aria-hidden='true'></em>Fair
     </div>
     " class="text-danger">
    {children}
  </a>
)

const Tag = ({tag, active, suggestion, onToggle}) => {
  const [quality] = suggestion || [-1];
  // using label buttons to fix focus issues with button
  return (
    <div className="btn-group" role="group">
      <label className={classnames('btn', 'btn-sm', 'ellipsis', {
                        'btn-success': quality >= 0,
                        'btn-default': quality < 0,
                        'active': active
                      })}
             type="button" onClick={onToggle}>
        <em className="glyphicon glyphicon-tag" aria-hidden="true"/>{tag}
        {quality >= 0 ?
          <ToolTip>
            <em className={classnames('glyphicon', 'quality', {
                              'glyphicon-star-empty': quality == 2,
                              'glyphicon-star': quality == 1,
                              'glyphicon-certificate': quality == 0
                             })}
                aria-hidden="true"/>
          </ToolTip> : null
        }
      </label>
    </div>
  )
}

const UrlText = ({text}) => {
  let matches = text.match(URL_PATTERN);
  if (matches) {
    return (
      <span>
        {_.zip(text.split(URL_PATTERN), matches).map(([frag, url], idx) => {
          return (<span key={idx}>{frag}<a href={url} target="_blank">{url}</a></span>);
        })}
      </span>
    );
  } else {
    return <span>{text}</span>
  }
}

const FBIcon = ({id}) => (
  <div className="col-xs-1 text-center fb-icon-col">
    <a href={"https://facebook.com/" + id}>
      <img src={"https://graph.facebook.com/" + id + "/picture?type=normal"}
           className="img-responsive img-rounded fb-icon"/>
    </a>
  </div>
)

const TagList = ({allTags, tags, suggestion, onDuplicate, onToggle, onNewTag}) => {
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
                      suggestion={_.find(suggestion, [1, tag])}
                      onToggle={() => onToggle(tag)}/>
        })}

        <div className="btn-group" role="group" key={"$$new$$"}>
          <input type="text" className="form-control new-tag input-sm" placeholder="new tag..."
                 ref={node => input = node}/>
        </div>
      </div>
    </form>
  )
}

const Tagger = ({id, user, page, message, tags, tagSet, suggestion, onDuplicate, onToggle, onNewTag}) => (
  <div className="container-fluid tagger">
    <div className="row">

      <FBIcon id={user.id}/>

      <div className="col-xs-10 fb-main">
        <h4 className="list-group-item-heading">
          <a href={"https://facebook.com/" + user.id}> {user.name} </a>
        </h4>
        <p className="list-group-item-text" id={'tagger-message-' + id}>
          <UrlText text={message}/>
        </p>
      </div>

      <FBIcon id={page}/>
    </div>
    <div className="row">
      <TagList allTags={_.union(tags, tagSet)}
               tags={tags}
               suggestion={suggestion}
               onDuplicate={onDuplicate}
               onNewTag={(tag) => onNewTag(tags, tag)}
               onToggle={(tag) => onToggle(tags, tag)}
      />
    </div>
  </div>
)

export default Tagger
