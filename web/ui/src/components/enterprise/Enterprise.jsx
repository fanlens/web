import _ from "lodash";
import React from "react";
import {Card, CardActions, CardHeader, CardMedia, CardTitle, CardText} from "material-ui/Card";
import Endless from "../Endless.jsx";
import Enquiry from "./Enquiry.jsx";
import "./Enterprise.css";

const Offer = ({head, tagline, features, theme, description, banner}) => (
  <Card className="offer">
    <CardTitle
      titleStyle={{color: 'white', textShadow: 'black 0px 0px 2px'}}
      className={theme + " darker offer-title"}
      title={head.replace('_', ' ')}/>
    <CardText className="offer-text">
      {description}
    </CardText>
    <CardMedia>
      <div className="offer-banner" style={{backgroundImage: `url(/static/img/${banner}-512.jpg)`}}/>
    </CardMedia>
    <CardHeader
      titleStyle={{color: 'white', textShadow: 'black 0px 0px 2px'}}
      className={theme + " lighter offer-header"}
      title={tagline}/>
  </Card>
);

const offers = [
  {
    head: "Enterprise",
    tagline: "Unleash Your Full Potential!",
    banner: 'lion-y',
    description: <section>
      <p><strong>No compromises!</strong> Kick your social media game into overdrive with
        our <strong>enterprise</strong> package.</p>
      <p>Get all the goodies from the Professional version and on top:</p>
      <ul>
        <li><strong>Unlimited</strong> Sources</li>
        <li><strong>Unlimited</strong> Users</li>
        <li><strong>Personal</strong> Instance</li>
      </ul>
      <p>Don't wait! Start your social media <strong>dominance!</strong></p>
    </section>,
    theme: 'theme-blue'
  },
  {
    head: "Reseller",
    tagline: "Your Clients, Your Advantage",
    banner: "lions-y",
    description: <section>
      <p>Want to pass the Fanlens mojo on to your clients? <strong>Great!</strong></p>
      <p>The <strong>Reseller's package</strong> allows you to do just that.
        Comprehensive <strong>discounts</strong> and redistribution /
        deviation <strong>rights</strong> allow you to integrate Fanlens.
      </p>
      <p>A <strong>Win/Win</strong> for everyone!</p>
      <p>Don't like the Fanlens branding? No problem, the <strong>Whitelabel</strong> doesn't require attribution!</p>
      <p>Get in touch and push your products to the next level!</p>
    </section>,
    theme: 'theme-red'
  },
  {
    head: "Special_Forces",
    tagline: "The Infinite Is Unkown",
    banner: "specops",
    description: <section>
      <p>
        Fanlens is not only a product, we are a highly motivated and skilled team that wants to <strong>solve your
        challenges!</strong></p>
      <p>We firmly believe that the only way to stay relevant is by working on
        <strong>real world</strong>
        use cases.</p>
      <p>Let's get in touch and see how we can <strong>work together</strong></p>
    </section>,
    theme: 'theme-violet'
  }];

const findOffer = (frag) => _.findIndex(offers, {head: frag.substring(1)});

const OffersList = ({initialIndex, onChangeIndex}) => (
  <Endless
    tight={true}
    theme={'light'}
    initialIndex={initialIndex}
    onChangeIndex={onChangeIndex}>
    {_.map(offers, (offer, idx) => <Offer key={idx} {...offer}/>)}
  </Endless>
);

const Team = () => (
  <div>
    <div id="team-bg"/>
    <div id="team"/>
  </div>
);

class Enterprise extends React.Component {
  render() {
    const frag = this.props.location.hash || ('#' + offers[0].head);
    const tag = frag.trim().substring(1).toLowerCase().replace(" ", "_");
    const offerIndex = Math.max(findOffer(frag), 0);
    return (
      <main id="legal" style={{display: 'flex', flexDirection: 'column', flex: '1 1 auto'}}>
        <Team/>
        <div id="offers-container" className="row end-sm center-xs">
          <div className="spacer col-lg-5 col-sm-4 col-xs-1"/>
          <div id="offers" className="col-lg-6 col-sm-7 col-xs-10">
            <OffersList
              initialIndex={offerIndex}
              onChangeIndex={(idx) => this.props.history.replace({
                pathname: this.props.location.pathname,
                hash: '#' + offers[idx].head
              })}/>
          </div>
          <div className="spacer col-lg-1 col-sm-1 col-xs-1"/>
        </div>
        <div id="signup" className="row end-lg middle-xs center-xs">
          <div className="spacer col-lg-5 col-xs-1"/>
          <Enquiry
            tag={tag}
            theme={offers[offerIndex].theme}/>
          <div className="spacer col-lg-1 col-xs-1"/>
        </div>
      </main>
    );
  }
}

export default Enterprise;
