import React from "react";
import {connect} from "react-redux";
import flow from "lodash/fp/flow";
import defaults from "lodash/fp/defaults";
import pickBy from "lodash/fp/pickBy";
import reduce from "lodash/fp/reduce";
import map from "lodash/fp/map";
import includes from "lodash/fp/includes";
import orderBy from "lodash/fp/orderBy";
import flatMap from "lodash/fp/flatMap";
import isEmpty from "lodash/fp/isEmpty";
import size from "lodash/fp/size";
import {GridList, GridTile} from "material-ui/GridList";
import {Card, CardActions, CardHeader, CardText} from 'material-ui/Card';
import FlatButton from 'material-ui/FlatButton';
import Avatar from "material-ui/Avatar";
import ActionBookmark from 'material-ui/svg-icons/action/bookmark';
import NavigationExpandMore from 'material-ui/svg-icons/navigation/expand-more';
import {fetchComments, toggleCommentTag} from '../../actions/ActivitiesActions';
import {strToCol} from "../stringUtils";

const mapIdx = map.convert({cap: false});

export const separators = {
  none: 0,
  hour: 3600,
  day: 86400,
  week: 604800
};

const tileCrunch = 6;
const tileBorder = '2px #409db1 solid';
const footerHeightCorrection = '1.3em';
const styles = {
  cellHeight: 235,
  tile: {},
  evenTile: {
    borderRight: tileBorder,
    marginRight: '-1px',
  },
  oddTile: {
    borderLeft: tileBorder,
    marginLeft: '-1px',
  },
  tileContent: {
    height: '65%',
    width: '100%',
    position: 'absolute',
    textAlign: 'center',
  },
  evenTileContent: {
    top: '2em',
  },
  oddTileContent: {
    top: '4.5em',
  },
  bubble: {
    borderRadius: '50%',
    width: '1em',
    height: '1em',
    marginTop: '2em',
    backgroundColor: '#409db1'
  },
  evenBubble: {
    float: 'right',
    marginRight: '-0.5em'
  },
  oddBubble: {
    float: 'left',
    marginLeft: '-0.5em'
  },
  topIndicator: {
    width: 0,
    height: 0,
    borderLeft: '0.75em solid transparent',
    borderRight: '0.75em solid transparent',
    borderTop: '0.75em solid rgb(64, 157, 177)',
  },
  evenTopIndicator: {
    float: 'right',
    marginRight: '-0.75em',
  },
  oddTopIndicator: {
    float: 'left',
    marginLeft: '-0.75em',
  },
};

const evenOdd = (idx, evenStyle, oddStyle, baseStyle = {}) => defaults(idx % 2 === 0 ? evenStyle : oddStyle)(baseStyle);
const tileStyle = (idx) => evenOdd(idx, styles.evenTile, styles.oddTile, styles.tile);
const bubbleStyle = (idx) => evenOdd(idx, styles.evenBubble, styles.oddBubble, styles.bubble);
const tileContentStyle = (idx) => evenOdd(idx, styles.evenTileContent, styles.oddTileContent, styles.tileContent);
const topIndicatorStyle = (idx) => evenOdd(idx, styles.evenTopIndicator, styles.oddTopIndicator, styles.topIndicator);

const resolveAvatar = (type) =>
  (id) => type === 'twitter' ?
    `https://twitter.com/${id}/profile_image?size=mini` :
    `https://graph.facebook.com/v2.8/${id}/picture?type=small`;

class Timeline extends React.Component {
  state = {
    highlightIdx: -1,
    expandedIdx: -1
  };

  render() {
    const {comments, tagSets, onMore, onToggleTag} = this.props;
    const numRows = Math.floor((Object.keys(comments).length + 1) / 2);
    return (
      <div>
        <GridList
          padding={0}
          cellHeight={styles.cellHeight}
          style={{
            height: `calc(${styles.cellHeight}px * ${numRows + (this.state.expandedIdx >= 0)} - ${tileCrunch}vh * ${numRows - 1})`,
            overflow: 'hidden',
          }}
          cols={2}>
          {
            flow(
              orderBy('created_time', 'desc'),
              mapIdx((comment, idx) => {
                return (
                  <GridTile
                    style={defaults({
                      marginTop: `${-Math.floor(idx / 2) * tileCrunch}vh`,
                    })(tileStyle(idx))}
                    rows={idx === this.state.expandedIdx ? 2 : 1}
                    key={idx}>
                    <div className="timeline-tile-content" style={
                      defaults(tileContentStyle(idx),
                        idx === this.state.expandedIdx && {
                          height: '75%'
                        })}>
                      <Card
                        expanded={this.state.expandedIdx === idx}
                        expandable={true}
                        onExpandChange={(expanded) => this.setState({expandedIdx: expanded ? idx : -1})}
                        onMouseOver={() => this.setState({highlightIdx: idx})}
                        zDepth={idx === this.state.highlightIdx || idx === this.state.expandedIdx ? 2 : 1}
                        rounded={true}
                        style={{
                          padding: '1em',
                          display: 'inline-block',
                          backgroundColor: 'white',
                          width: '90%',
                          height: '100%',
                          textAlign: 'left',
                          overflow: 'scroll',
                          cursor: 'hand',
                        }}>
                        {flow(
                          pickBy((score) => score > 0.5),
                          map.convert({cap: false})((score, tag) => (
                            <div key={tag} style={{float: 'right'}}>
                              <ActionBookmark role="img" aria-label={tag}
                                              style={{color: strToCol(tag), margin: '-0.5em -0.5em 0 0'}}/>
                            </div>)
                          ))(comment.prediction)}
                        <CardHeader
                          style={{padding: 0, margin: 0}}
                          title={comment.user.name || comment.user.id}
                          actAsExpander={true}
                          subtitle={`on ${new Date(comment.created_time).toLocaleString()}`}
                          avatar={
                            <Avatar
                              backgroundColor='transparent'
                              src={resolveAvatar(comment.source.type)(comment.user.id)}/>}
                        />
                        <CardActions expandable={true} style={{textAlign: 'center', padding: 0}}>
                          {flatMap((tagSet) => tagSet.tags.map((tag, idx) => {
                            const isTagged = includes(tag)(comment.tags);
                            return (
                              <FlatButton
                                key={idx}
                                primary={isTagged}
                                onTouchTap={() => onToggleTag(comment, tag)}
                                icon={
                                  <ActionBookmark
                                    role="img"
                                    aria-label={tag}
                                    style={{fill: strToCol(tag), marginRight: '-0.4em'}}/>
                                }
                                label={tag + (comment.prediction[tag] > 0.5 ? '*' : '')}/>
                            )
                          }))(tagSets)}
                        </CardActions>
                        <CardText
                          actAsExpander={true}
                          style={{padding: '0.125em 0 0 0', margin: 0}}
                        >
                          {comment.text}
                        </CardText>
                      </Card>
                      <div className="timeline-bubble" style={bubbleStyle(idx)}/>
                    </div>
                    {idx < 2 &&
                    <div className="timeline-top-indicator" style={topIndicatorStyle(idx)}/>}
                  </GridTile>
                )
              })
            )(comments)}
        </GridList>
        {!isEmpty(comments) &&
        <FlatButton
          style={{width: '100%', color: '#409db1', marginBottom: footerHeightCorrection}}
          icon={<NavigationExpandMore/>}
          onTouchTap={() => onMore({count: Math.ceil(size(comments) * 1.5)})}
        />}
      </div>
    );
  }
}

const mapStateToProps = (state) => defaults({
  comments: state.activities.comments,
  sources: state.activities.sources,
})(state.app.timeline);

const mapDispatchToProps = (dispatch) => ({
  onToggleTag: (comment, tag) => dispatch(toggleCommentTag(comment, tag)),
  fetchComments: (args) => dispatch(fetchComments(defaults(args)({
    since: new Date(args.since).toISOString(),
    until: new Date(args.until).toISOString()
  }))),
});

const mergeProps = (stateProps, dispatchProps, ownProps) => reduce(defaults, {})([
  ownProps,
  stateProps,
  dispatchProps,
  {
    onMore: (args = {}) => dispatchProps.fetchComments(defaults(stateProps)(args)),
  }
]);

export default connect(mapStateToProps, mapDispatchToProps, mergeProps)(Timeline);

