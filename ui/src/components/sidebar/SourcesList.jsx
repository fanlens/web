import React from 'react';
import {connect} from 'react-redux';
import _ from 'lodash';

import {List, ListItem} from 'material-ui/List';
import Checkbox from 'material-ui/Checkbox';
import FontIcon from 'material-ui/FontIcon';
import SvgIconInbox from "material-ui/svg-icons/content/inbox";
import Avatar from 'material-ui/Avatar';

function iconFromType(type) {
  switch (type) {
    case 'twitter':
      return 'fa-twitter';
    case 'facebook':
      return 'fa-facebook-square';
    default:
      return 'fa-star';
  }
}

function avatarFromType(type, slug) {
  switch (type) {
    case 'twitter':
      return `https://twitter.com/${slug}/profile_image?size=normal`
    case 'facebook':
      return `https://graph.facebook.com/${slug}/picture`
    default:
      return '/static/img/logo.png';
  }
}

const SourcesList = ({initiallyOpen = false, sources}) => (
  <List>
    <ListItem
      primaryText="Sources"
      initiallyOpen={initiallyOpen}
      leftIcon={<SvgIconInbox />}
      nestedItems={_.map(sources, (source) => (
        <ListItem
          key={source.id}
          primaryText={
            <span>
              <FontIcon style={{fontSize: '1em'}}
                        className={`fa ${iconFromType(source.type)}`}/> {source.slug}
            </span>
          }
          secondaryText={source.uri}
          leftCheckbox={<Checkbox checked={true} disabled={true}/>}
          rightAvatar={<Avatar src={avatarFromType(source.type, source.slug)}/>}
        />
      ))}
    />
  </List>
);

const mapStateToProps = (state) => ({
  sources: state.activities.sources,
});

export default connect(mapStateToProps)(SourcesList)
