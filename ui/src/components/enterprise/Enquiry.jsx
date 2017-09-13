import React from "react";
import {connect} from "react-redux";
import Paper from "material-ui/Paper";
import TextField from "material-ui/TextField";
import RaisedButton from "material-ui/RaisedButton";
import {sendEnquiry} from "../../actions/app/email";

const emailPattern = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
const emailValidator = (email) => emailPattern.test(email); // not curryable

class Enquiry extends React.Component {
  state = {email: '', error: true};

  render() {
    const {theme, onSendEnquiry} = this.props;
    return (
      <Paper className="signup-fields col-lg-6 col-xs-10">
        <div className="row middle-xs center-xs">
          <div className="col-sm col-xs-12">
            <TextField
              hintText="jane@example.com"
              className={theme + " darker no-bg"}
              floatingLabelText="Enter your Email"
              onChange={(evt, newValue) => this.setState({
                email: newValue,
                error: !emailValidator(newValue)
              })
              }
              fullWidth={true}
            />
          </div>
          <div className="col-sm-3 col-xs-12">
            <RaisedButton
              label="Enquire"
              className={theme + " darker"}
              primary={true}
              fullWidth={true}
              disabled={this.state.error}
              onTouchTap={() => onSendEnquiry(this.state.email)}
            />
          </div>
        </div>
      </Paper>
    );
  }
}

const mapStateToProps = () => ({});

const mapDispatchToProps = (dispatch, {tag}) => ({
  onSendEnquiry: (email) => dispatch(sendEnquiry(tag, email))
});

export default connect(mapStateToProps, mapDispatchToProps)(Enquiry)