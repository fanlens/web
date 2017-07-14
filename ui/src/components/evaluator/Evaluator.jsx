import React from "react";
import {connect} from "react-redux";
import defaults from "lodash/fp/defaults";
import reduce from "lodash/fp/reduce";
import isEmpty from "lodash/fp/isEmpty";
import map from "lodash/fp/map";
import Paper from 'material-ui/Paper';
import TextField from 'material-ui/TextField';
import RaisedButton from 'material-ui/RaisedButton';
import FlatButton from 'material-ui/FlatButton';
import ContentSend from 'material-ui/svg-icons/content/send';
import ActionGavel from 'material-ui/svg-icons/action/gavel';
import ActionWatchLater from 'material-ui/svg-icons/action/watch-later';
import ActionHourglassEmpty from 'material-ui/svg-icons/action/hourglass-empty';
import ActionBookmark from 'material-ui/svg-icons/action/bookmark';
import {fetchSuggestionForText, clearSuggestion, setIsFetching} from "../../actions/ModelActions";
import {strToCol} from "../stringUtils";

class Evaluator extends React.Component {
  state = {text: ''};

  componentWillReceiveProps(nextProps) {
    const {suggestion} = nextProps;
    if (!isEmpty(suggestion)) {
      this.setState({text: suggestion.text});
    }
  }

  render() {
    const {
      isFetching, onEvaluate, suggestion
    } = this.props;
    return (
      <div className="row center-sm middle-sm" style={{margin: '0.5em 0'}}>
        <div className="col-sm-8 col-xs">
          <Paper zDepth={2} style={{padding: '0.5em 1em', textAlign: 'left'}}>
            <div className="row">
              <div className="col-xs">
                <TextField
                  fullWidth={true}
                  rowsMax={10}
                  multiLine={true}
                  autoFocus={true}
                  hintText="Example: Hey folks how's it going?! (min. 24 characters)"
                  floatingLabelText={`Enter A New Post${this.state.text.length > 0 && this.state.text.length < 24 ? ` ${24-this.state.text.length} more` : ''}`}
                  onChange={(_, text) => this.setState({text})}
                  value={this.state.text}
                />
              </div>
            </div>
            <div className="row">
              <div className="col-sm col-xs-12">
                <RaisedButton
                  label="Evaluate"
                  icon={isFetching ? <ActionHourglassEmpty/> : <ActionGavel/>}
                  disabled={isFetching || this.state.text.length < 24}
                  primary={true}
                  fullWidth={true}
                  onTouchTap={() => onEvaluate({text: this.state.text})}
                />
              </div>
              <div className="col-sm col-xs-12">
                <RaisedButton
                  label="Post Now"
                  icon={<ContentSend/>}
                  secondary={true}
                  fullWidth={true}
                  disabled={true}
                />
              </div>
              <div className="col-sm col-xs-12">
                <RaisedButton
                  label="Schedule"
                  icon={<ActionWatchLater/>}
                  fullWidth={true}
                  disabled={true}
                />
              </div>
            </div>
            {!isEmpty(suggestion) &&
            <div className="row center-xs middle-xs" style={{marginTop: '0.5em'}}>
              {map.convert({cap: false})((score, tag) => (
                <div
                  className="col-xs"
                  key={tag}
                >
                  <FlatButton
                    fullWidth={true}
                    icon={
                      <ActionBookmark
                        role="img"
                        aria-label={tag}
                        style={{fill: strToCol(tag), marginRight: '-0.4em'}}/>
                    }
                    label={`${tag} ${Math.round(score * 10000) / 100}%`}/>
                </div>
              ))(suggestion.prediction)}
            </div>
            }
          </Paper>
        </div>
      </div>
    );
  }
}


const mapStateToProps = (state) => defaults({
  sources: state.app.timeline.sources,
  tagSets: state.app.timeline.tagSets,
})(state.app.evaluator);

const mapDispatchToProps = (dispatch) => ({
  fetchSuggestionForText: (args) => dispatch(setIsFetching(true))
    .then(dispatch(clearSuggestion()))
    .then(dispatch(fetchSuggestionForText(args)))
});

const mergeProps = (stateProps, dispatchProps, ownProps) => reduce(defaults, {})([
  ownProps,
  stateProps,
  dispatchProps,
  {
    onEvaluate: (args) => dispatchProps.fetchSuggestionForText(defaults(stateProps)(args)),
  }
]);

export default connect(mapStateToProps, mapDispatchToProps, mergeProps)(Evaluator);