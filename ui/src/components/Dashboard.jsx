import React from "react";
import {connect} from "react-redux";
import _ from "lodash";
import "./Eev.css";
import {GridList, GridTile} from "material-ui/GridList";
import Avatar from "material-ui/Avatar";
import Chip from "material-ui/Chip";
import SvgTag from "material-ui/svg-icons/maps/local-offer";
import {Card, CardActions, CardHeader, CardText} from "material-ui/Card";
import {fetchRandomCommentsTagSet, initActivities} from "../actions/ActivitiesActions";

const styles = {
  root: {
    margin: '1em',
    display: 'flex',
    flexWrap: 'wrap',
    flex: '0 0 auto',
    justifyContent: 'space-around',
  },
  gridList: {
    width: '100%',
    overflowY: 'scroll',
  },
};

const resolveAvatar = (type) =>
  (id) => type === 'twitter' ?
    `https://twitter.com/${id}/profile_image?size=mini` :
    `https://graph.facebook.com/v2.8/${id}/picture?type=small`;

const tileHeight = 180;
const tileWidth = 360;

const Comment = ({comment}) => (
  <Card style={{textAlign: 'left', height: '100%', display: 'flex'}}
        containerStyle={{display: 'flex', flexDirection: 'column', width: '100%'}}>
    <CardHeader
      title={comment.user.name}
      subtitle={`at ${comment.created_time}`}
      avatar={<Avatar backgroundColor='transparent' src={resolveAvatar(comment.source.type)(comment.user.id)}/>}
      style={{flex: '0 1 auto', paddingBottom: '0.5em'}}/>
    <CardText style={{paddingTop: 0, flex: '1 1 auto', overflowY: 'scroll'}}>
      {comment.text}
    </CardText>
    <CardActions style={{flex: '0 1 auto', textAlign: 'right'}}>
      {_.map(
        _.defaults(comment.prediction,
          _.chain(comment.tags)
            .keyBy()
            .mapValues(_ => 0)
            .value()),
        (score, tag) => (
          <Chip key={tag} style={{display: 'inline-flex'}}>
            <Avatar
              color={score >= 0.75 ? 'green' : score >= 0.5 ? 'orange' : score > 0 ? 'grey' : 'red'}
              icon={<SvgTag />}/>
            {tag} {Math.round(score * 100)}% {_.includes(comment.tags, tag) && (score > 0.5 ? '✓' : '⚡')}
          </Chip>
        ))}
    </CardActions>
  </Card>
);

class Dashboard extends React.Component {
  state = {width: '10', height: '10'};
  _updateWindowDimensions = () => this.setState({width: window.innerWidth, height: window.innerHeight});

  componentDidMount() {
    this.props.init();
    this._updateWindowDimensions();
    window.addEventListener('resize', this._updateWindowDimensions);
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this._updateWindowDimensions);
  }

  render() {
    const {comments, sources} = this.props;
    const count = Math.floor(this.state.height / tileHeight) * Math.floor(this.state.width / tileWidth)
    const onFetch = () => count && this.props.onFetch(count, sources);
    if (_.values(comments).length === 0) {
      onFetch();
    }
    return (
      <main id="legal" style={{display: 'flex', flexDirection: 'column', flex: '1 1 auto', overflowY: 'scroll'}}>
        <div style={styles.root}>
          <GridList
            padding={12}
            cellHeight={tileHeight}
            style={styles.gridList}
            cols={Math.floor(this.state.width / tileWidth)}>
            {_.map(comments, (comment, idx) => (
              <GridTile
                onTouchTap={onFetch}
                key={idx}>
                <Comment comment={comment}/>
              </GridTile>
            ))}
          </GridList>
        </div>
      </main>
    );
  }
}

const mapStateToProps = (state) => ({
  comments: state.activities.comments,
  // sources: state.activities.sources,
  sources: _.pickBy(state.activities.sources, (_, k) => k == 9),
});

const mapDispatchToProps = (dispatch) => ({
  init: (force = false) => dispatch(initActivities(force)),
  //onFetch: (count, sources) => (_.values(sources).length > 0) && dispatch(fetchRandomComments(count, sources))
  onFetch: (count, sources) => dispatch(fetchRandomCommentsTagSet(count, 6))
});

export default connect(mapStateToProps, mapDispatchToProps)(Dashboard);
