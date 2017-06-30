import React from "react";
import {connect} from "react-redux";
import flow from "lodash/fp/flow";
import defaults from "lodash/fp/defaults";
import map from "lodash/fp/map";
import sortBy from "lodash/fp/sortBy";
import {GridList, GridTile} from "material-ui/GridList";
import {Card, CardHeader, CardText} from 'material-ui/Card';
import Avatar from "material-ui/Avatar";

const mapIdx = map.convert({cap: false});

export const separators = {
  none: 0,
  hour: 3600,
  day: 86400,
  week: 604800
};

const tileCrunch = 6;
const tileOffset = 30;
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
    bottom: `${tileOffset}%`,
  },
  oddTileContent: {
    top: `${tileOffset}%`,
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
  bottomIndicator: {
    width: 0,
    height: 0,
    position: 'absolute',
    bottom: 0,
    borderLeft: '0.75em solid transparent',
    borderRight: '0.75em solid transparent',
    borderBottom: '0.75em solid rgb(64, 157, 177)',
  },
  evenBottomIndicator: {
    float: 'right',
    right: '-0.75em',
  },
  oddBottomIndicator: {
    float: 'left',
    left: '-0.75em',
  },
};

const evenOdd = (idx, evenStyle, oddStyle, baseStyle = {}) => defaults(idx % 2 === 0 ? evenStyle : oddStyle)(baseStyle);
const tileStyle = (idx) => evenOdd(idx, styles.evenTile, styles.oddTile, styles.tile);
const bubbleStyle = (idx) => evenOdd(idx, styles.evenBubble, styles.oddBubble, styles.bubble);
const tileContentStyle = (idx) => evenOdd(idx, styles.evenTileContent, styles.oddTileContent, styles.tileContent);
const topIndicatorStyle = (idx) => evenOdd(idx, styles.evenTopIndicator, styles.oddTopIndicator, styles.topIndicator);
const bottomIndicatorStyle = (idx) => evenOdd(idx, styles.evenBottomIndicator, styles.oddBottomIndicator, styles.bottomIndicator);

const resolveAvatar = (type) =>
  (id) => type === 'twitter' ?
    `https://twitter.com/${id}/profile_image?size=mini` :
    `https://graph.facebook.com/v2.8/${id}/picture?type=small`;

const Timeline = ({comments, separator = separators.day}) => {
  const numRows = Math.floor((Object.keys(comments).length + 1) / 2);
  return (
    <GridList
      padding={0}
      cellHeight={styles.cellHeight}
      style={{
        height: `calc(${styles.cellHeight}px * ${numRows} - ${tileCrunch}vh * ${numRows - 1} + ${footerHeightCorrection})`,
        overflow: 'hidden',
      }}
      cols={2}>
      {
        flow(
          sortBy((comment) => comment.created_time),
          mapIdx((comment, idx) => {
            return (
              <GridTile
                style={defaults({
                  marginTop: `${-Math.floor(idx / 2) * tileCrunch}vh`
                })(tileStyle(idx))}
                key={idx}>
                <div className="timeline-tile-content" style={tileContentStyle(idx)}>
                  <Card
                    expanded={true}
                    zDepth={1}
                    rounded={true}
                    style={{
                      padding: '1em',
                      display: 'inline-block',
                      backgroundColor: 'white',
                      width: '90%',
                      height: '100%',
                      textAlign: 'left',
                      overflow: 'scroll',
                    }}>
                    <CardHeader
                      style={{padding: 0, margin: 0}}
                      title={comment.user.name || comment.user.id}
                      subtitle={`on ${new Date(comment.created_time).toLocaleString()}`}
                      avatar={
                        <Avatar
                          backgroundColor='transparent'
                          src={resolveAvatar(comment.source.type)(comment.user.id)}/>}
                    />
                    <CardText
                      style={{padding: '0.125em 0 0 0', margin: 0}}
                    >
                      {comment.text}
                      {map.convert({cap: false})((score, tag) => (
                        <div key={tag}>
                          {tag}
                        </div>
                      ))(comment.prediction)}
                    </CardText>
                  </Card>
                  <div className="timeline-bubble" style={bubbleStyle(idx)}/>
                </div>
                {idx < 2 &&
                <div className="timeline-top-indicator" style={topIndicatorStyle(idx)}/>}
                {idx >= (numRows - 1) * 2 &&
                <div className="timeline-bottom-indicator" style={bottomIndicatorStyle(idx)}/>}
              </GridTile>
            )
          })
        )(comments)}
    </GridList>
  );
};

const mapStateToProps = (state) => ({
  comments: state.activities.comments,
});

const mapDispatchToProps = (dispatch) => ({});

export default connect(mapStateToProps, mapDispatchToProps)(Timeline);
