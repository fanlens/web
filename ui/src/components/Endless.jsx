import React from "react";
import SwipeableViews from "react-swipeable-views";
import {bindKeyboard, virtualize} from "react-swipeable-views-utils";
import IconButton from "material-ui/IconButton";
import SVGNavPrev from "material-ui/svg-icons/image/navigate-before";
import SVGNavNext from "material-ui/svg-icons/image/navigate-next";

const randomInt = (min, max) => {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min)) + min;
};

const VirtualizeSwipeableViews = bindKeyboard(virtualize(SwipeableViews));


const rgba = (amount) => `rgba(${new Array(3).fill(amount).join()}, 0.87)`;
const arrowColor = (theme) => rgba(theme === 'light' ? 255 : 0);

class Endless extends React.Component {
  state = {index: 0, offset: randomInt(0, 100)};
  idxMapper = (index) => {
    const offset = this.props.random ? this.state.offset : 0;
    return (Math.abs(index) + offset) % this.props.children.length;
  };
  _onChangeIndex = (index) => {
    this.setState({index});
    this.props.onChangeIndex && this.props.onChangeIndex(this.idxMapper(index));
  };
  _next = () => this._onChangeIndex(this.state.index + 1, this.state.index);
  _prev = () => this._onChangeIndex(this.state.index - 1, this.state.index);

  slideRenderer = ({key, index}) => (
    <div key={key}>
      {this.props.children[this.idxMapper(index)]}
    </div>
  );

  render() {
    return (
      <div className="row middle-xs">
        <div className={`col-xs-2 ${this.props.tight ? 'end' : 'start'}-xs`}>
          <IconButton
            onTouchTap={this._prev}>
            <SVGNavPrev color={arrowColor(this.props.theme)}/>
          </IconButton>
        </div>
        <div className="col-xs-8">
          <VirtualizeSwipeableViews
            index={this.state.index}
            onChangeIndex={this._onChangeIndex}
            slideRenderer={this.slideRenderer}/>
        </div>
        <div className={`col-xs-2 ${this.props.tight ? 'start' : 'end'}-xs`}>
          <IconButton
            onTouchTap={this._next}>
            <SVGNavNext color={arrowColor(this.props.theme)}/>
          </IconButton>
        </div>
      </div>
    );
  }
}

export default Endless;
