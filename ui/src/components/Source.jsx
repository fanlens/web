import React from 'react'
import classnames from 'classnames'

export const userUri = (id, type) => {
  switch (type) {
    case 'facebook':
      return 'https://facebook.com/' + id;
    case 'twitter':
      return 'https://twitter.com/' + id;
    default:
      return '#'
  }
};

export const iconUri = (id, type) => {
  switch (type) {
    case 'facebook':
      return `https://graph.facebook.com/${id}/picture?type=normal`;
    case 'twitter':
      return `https://twitter.com/${id}/profile_image?size=normal`;
    default:
      return '#'
  }
};

export const Icon = ({id, type}) =>(
  <div className="col-xs-1 text-center fb-icon-col">
    <a href={userUri(id, type)}>
      <img src={iconUri(id, type)}
           className="img-responsive img-rounded fb-icon"/>
    </a>
  </div>
);

export const UserLink = ({user, type}) => <a href={userUri(user.id, type)}>{user.name}</a>;

export const iconFromSourceType = (type) => {
  switch (type) {
    case 'facebook':
      return 'fa-facebook-official';
    case 'twitter':
      return 'fa-twitter-square';
    default:
      return 'fa-folder';
  }
};

export const SourceIcon = ({type}) => <em className={classnames('fa', iconFromSourceType(type))}/>;


const SourceElement = ({source}) =>(
  <div className="ellipsis">
    <img className="fb-sources-icon" src={iconUri(source.slug, source.type)}/>
    <span className="fb-sources-text"> <SourceIcon type={source.type}/> <strong>{source.slug}</strong> </span>
  </div>
);

export default SourceElement
