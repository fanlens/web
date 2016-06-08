import React from 'react';
import _ from 'lodash';
import classnames from 'classnames'


const URL_PATTERN = /(?:(?:http|ftp|https):\/\/)?(?:[\w_-]+(?:(?:\.[\w_-]+)+))(?:[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?/gi;

function adjustFade(id) {
  let message = $('#tagger-message-' + id);
  if (message.prop('scrollTop') + message.height() == message.prop('scrollHeight')) {
    message.removeClass('fade-bottom');
  } else {
    if (message.prop('offsetHeight') < message.prop('scrollHeight')) {
      message.addClass('fade-bottom');
    }
  }
}

const ToolTip = ({children}) => (
  <a href="#" rel="tooltip" data-container="body" data-toggle="tooltip" data-html="true" data-delay="300"
     title="<p>
     Confidence<br/>
     <span class='glyphicon glyphicon-certificate' aria-hidden='true'></span> Excellent
     <span class='glyphicon glyphicon-star' aria-hidden='true'></span> Good
     <span class='glyphicon glyphicon-star-empty' aria-hidden='true'></span> Fair
     </p>
     ">
    {children}
  </a>
)

const Tag = ({tag, active, suggestion, onToggle}) => {
  const [suggPercent] = suggestion || [0];
  const suggested = suggPercent > 0.7;
  return (
    <div className="btn-group" role="group">
      <button className={classnames('btn', 'ellipsis', {
                        'btn-primary': suggested,
                        'btn-default': !suggested,
                        'active': active
                      })}
              type="button" onClick={onToggle}>
        <span className="glyphicon glyphicon-tag" aria-hidden="true"></span> {tag}
        {suggested ?
          <ToolTip>
            <span className={classnames('glyphicon', {
                              'glyphicon-star-empty': suggPercent <= 0.95,
                              'glyphicon-star': 0.95 < suggPercent && suggPercent <= 0.99,
                              'glyphicon-certificate': 0.99 < suggPercent
                             })}
                  style={{marginLeft: '0.25em', marginTop:'0.10em'}}>
            </span>
          </ToolTip> : null
        }
      </button>
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

const TagList = ({allTags, tags, suggestion, onDuplicate, onToggle}) => {
  let input;
  return (
    <form className="form-group" onSubmit={ e => {
          e.preventDefault();
          const newTag = input.value.trim()
          if (newTag && newTag != '$$new$$') {
            if (_.includes(allTags, newTag)) {
              onDuplicate(`The entered tag ${newTag} is a duplicate!`)
            } else {
              onToggle(newTag)
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
          <input type="text" className="form-control new-tag" placeholder="new tag..." ref={node => input = node}/>
        </div>
      </div>
    </form>
  )
}

const Tagger = ({id, user, page, message, tags, tagSet, suggestion, onDuplicate, onToggle}) => (
  <div className="container-fluid">
    <div className="row">

      <FBIcon id={user.id}/>

      <div className="col-xs-10 fb-main">
        <h4 className="list-group-item-heading">
          <a href={"https://facebook.com/" + user.id}> {user.name} </a>
        </h4>
        <p className="list-group-item-text" onScroll={() => adjustFade(id)}
           id={'tagger-message-' + id}>
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
               onToggle={(tag) => onToggle(tags, tag)}
      />
    </div>
  </div>
)

const ResponsiveTagger = React.createClass({
  componentDidMount() {
    window.addEventListener('resize', () => adjustFade(this.props.id));
  },

  componentWillUnmount() {
    window.removeEventListener('resize', () => adjust(this.props.id));
  },

  render() {
    return <Tagger {...this.props} />
  }
});

export default ResponsiveTagger
