import React from "react";
import {connect} from "react-redux";
import {Link} from "react-router-dom";
import map from "lodash/fp/map";
import head from "lodash/fp/head";
import reduce from "lodash/fp/reduce";
import isEmpty from "lodash/fp/isEmpty";
import defaults from "lodash/fp/defaults";
import Paper from 'material-ui/Paper';
import DropDownMenu from 'material-ui/DropDownMenu';
import MenuItem from 'material-ui/MenuItem';
import ActionTimeline from 'material-ui/svg-icons/action/timeline';
import FloatingActionButton from 'material-ui/FloatingActionButton';
import * as tlActions from "../../actions/app/timeline";


const controlHeight = '3em';
const ControlFrame = ({className, children}) => (
  <Paper className={className} zDepth={1} rounded={true}
         style={{
           textAlign: 'center',
           display: 'inline-block',
           padding: '0 0.5em',
           width: '100%',
           height: controlHeight
         }}>
    {children}
  </Paper>
);

class EvaluatorControls extends React.Component {
  componentWillReceiveProps(nextProps) {
    const {allTagSets, setTagSets, allSources, setSources} = nextProps;
    if (isEmpty(this.props.tagSets) && !isEmpty(allTagSets)) {
      setTagSets(take(1, values(allTagSets)))
    }
    if (isEmpty(this.props.sources) && !isEmpty(allSources)) {
      setSources(take(1, values(allSources)))
    }
  }

  render() {
    const {allTagSets, tagSets, allSources, sources, onSelectTagSet, onSelectSource} = this.props;
    return (
      <div className="row center-xs middle-xs" style={{padding: '0 0.5em 0.5em 0.5em', overflow: 'hidden'}}>
        <div className="col-lg-4 col-sm-6 col-xs-12">
          <div style={{height: '3em', marginTop: '0.5em'}}>
            <ControlFrame>
              <DropDownMenu
                style={{height: '3em', marginTop: '-0.31em', width: '100%'}}
                value={isEmpty(sources) ? -1 : head(sources).id}
                disabled={isEmpty(allSources)}
                onChange={(_, __, selectedSourceId) => onSelectSource(selectedSourceId)}
                autoWidth={false}
                multiple={false}
              >
                {map(({id, type, slug}) => (
                  <MenuItem key={id} value={id} primaryText={`${type} > ${slug}`}/>)
                )(allSources)}
              </DropDownMenu>
            </ControlFrame>
          </div>
        </div>
        <div className="col-lg-4 col-sm-6 col-xs-12">
          <div style={{height: '3em', marginTop: '0.5em'}}>
            <ControlFrame>
              <DropDownMenu
                style={{height: '3em', marginTop: '-0.31em', width: '100%'}}
                value={isEmpty(tagSets) ? -1 : head(tagSets).id}
                disabled={isEmpty(allTagSets)}
                onChange={(_, __, selectedTagsetId) => onSelectTagSet(selectedTagsetId)}
                autoWidth={false}
                multiple={false}
              >
                {map(({id, title}) => (
                  <MenuItem key={id} value={id} primaryText={title}/>)
                )(allTagSets)}
              </DropDownMenu>
            </ControlFrame>
          </div>
        </div>

        <Link to="/v4/ui/timeline" style={{
          float: 'right',
          position: 'fixed',
          right: '8px',
          bottom: '92px',
          zIndex: 10000
        }}>
          <FloatingActionButton>
            <ActionTimeline style={{transform: 'rotate(135deg)'}}/>
          </FloatingActionButton>
        </Link>
      </div>
    );
  }
}

const mapStateToProps = (state) => defaults({
  allTagSets: state.activities.tagSets,
  allSources: state.activities.sources,
})(state.app.timeline);

const mapDispatchToProps = (dispatch) => ({
  setTagSets: (tagSets) => dispatch(tlActions.setTagSets(tagSets)),
  setSources: (sources) => dispatch(tlActions.setSources(sources)),
});

const mergeProps = (stateProps, dispatchProps, ownProps) => reduce(defaults, {})([
  ownProps,
  stateProps,
  dispatchProps,
  {
    onSelectTagSet: (id) => dispatchProps.setTagSets([stateProps.allTagSets[id]]),
    onSelectSource: (id) => dispatchProps.setSources([stateProps.allSources[id]]),
  }
]);

export default connect(mapStateToProps, mapDispatchToProps, mergeProps)(EvaluatorControls);