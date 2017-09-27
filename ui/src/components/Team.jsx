import _ from "lodash";
import React from "react";
import {Card, CardActions, CardHeader, CardMedia, CardTitle, CardText} from "material-ui/Card";
import FlatButton from "material-ui/FlatButton";
import FontIcon from "material-ui/FontIcon";
import Endless from "./Endless.jsx";
import Avatar from "material-ui/Avatar";
import './Team.css';

const firstUpper = (str) => str.charAt(0).toUpperCase() + str.slice(1);

export const TeamMember = ({name, tagline, role, roleDescription, img, bio, social}) => (
  <Card style={{textAlign: 'left'}}>
    <CardHeader
      title={`${role} - ${name}`}
      titleStyle={{marginTop: 'calc(72px / 6)'}}
      subtitle={tagline}
      avatar={<Avatar src={`/static/img/${img}-128.jpg`} size={72}/>}
      actAsExpander={true}
      showExpandableButton={true}
    />
    <CardMedia expandable={true} mediaStyle={{textAlign: 'center'}}>
      <img src={`/static/img/${img}-512.jpg`} style={{minWidth: '75%', width: '75%'}}/>
    </CardMedia>
    <CardTitle expandable={true} title={roleDescription} style={{padding: '8px 16px 0px 16px'}}/>
    <CardText expandable={true} style={{padding: '0 16px'}}>
      {_.map(bio, (line, idx) => <p key={idx}>{line}</p>)}
    </CardText>
    <CardActions expandable={true} style={{textAlign: 'center'}}>
      {_.map(social, (url, network) => <FlatButton
          key={url}
          target="_blank"
          label={firstUpper(network)}
          href={url}
          icon={<FontIcon className={`fa fa-${network}`}/>}
        />
      )}
    </CardActions>
  </Card>
);

const Team = () => (
  <div className="row top-md center-md">
    {_.map([
      {
        name: "Christian Junker",
        tagline: "Hacker, researcher, entrepreneur... something like that.",
        role: "CEO",
        roleDescription: "Chief Everything Officer",
        img: "chris",
        bio: [
          "Christian is a lifelong hacker, entrepreneur and researcher, and has over 10 years of experience mainly in the fields of data science and big data.",
          "This is his 2nd startup, he was the former CTO of visalyze where he successfully led a team through multiple rounds of public fundings and research grants. He hiked Camino de Santiago from his doorstep and travelled around the world. Afterwards he helped to restructure multiple IT companies and briefly returned to research before founding Fanlens.",
          "Christian holds an MSc in Computer Science (with distinction) from the Johannes Kepler Universität Linz and a BSc in Biomedical Informatics from the Private Universität für Gesundheitswissenschaften, Medizinische Informatik und Technik."
        ],
        social: {
          facebook: 'https://facebook.com/chjdev',
          twitter: 'https://twitter.com/chjdev',
          linkedin: 'https://linkedin.com/in/chjdev',
        }
      },
      {
        name: "Martí Cuquet Palau",
        tagline: "Mad Scientist-in-Chief",
        role: "CSO",
        roleDescription: <span>Chief <span style={{fontFamily: 'serif', letterSpacing: '0.05em'}}>Σ<i>
            <sub style={{marginLeft: '-0.05em'}}>c</sub><sup
          style={{
            marginLeft: '-0.5em',
            marginRight: '0.25em'
          }}>i</sup>e<sup>n</sup>c<sup>e</sup></i></span> Officer</span>,
        img: "marti",
        bio: [
          "Martí was Senior Postdoctoral Researcher at Semantic Technology Institute, Universität Innsbruck, and joined as Chief Science Officer.",
          "He has over 9 years of experience in research. He has been a Postdoctoral Researcher at Universität Innsbruck, first in quantum information and entanglement theory at the Institut für Theoretische Physik, and later in big data, data science and its social implications in the Semantic Technology Institute. He has been involved in several research projects at the European, Austrian and Spanish level. He recently led the design of projects in complex networks and machine learning in the tourism sector, and prepared a research roadmap for societal impact of big data in Europe in the framework of the EU FP7 BYTE project.",
          "He holds a Ph.D. in Physics from Universitat Autònoma de Barcelona (2012, Extraordinary Doctoral Award), with research at the crossroads of quantum information theory and network science."
        ],
        social: {
          facebook: 'https://facebook.com/mcuquet',
          twitter: 'https://twitter.com/mcuquet',
          linkedin: 'https://linkedin.com/in/mcuquet',
        }
      }
    ], (member, idx) => (
      <div key={idx} className="col-md-5 col-xs-12" style={{marginBottom: '16px'}}>
        <TeamMember {... member} />
      </div>
    ))}
  </div>
);

const Customer = ({name, context, href, comment, img, imgType = 'jpg'}) => (
  <Card style={{textAlign: 'left', boxShadow: 'none'}}>
    <CardHeader
      title={name}
      titleStyle={{marginTop: 'calc(72px / 6)'}}
      subtitle={<a href={href} target="_blank">{context}</a>}
      avatar={<Avatar src={`/static/img/${img}-128.jpg`} size={72}/>}
    />
    <CardText style={{paddingTop: 0}}>
      "{comment}"
    </CardText>
  </Card>
);

const Customers = () => (
  <div className="row top-xs center-xs">
    <div className="col-md-7 col-xs-12" style={{marginBottom: '16px'}}>
      <Card style={{textAlign: 'left'}}>
        <CardHeader title="A Word from Our Customers"/>
        <Endless random={true} tight={true}>
          {_.map([
            {
              name: "Allan Lund Hansen",
              context: "CEO of Sirenio",
              href: "https://sirenio.com",
              comment: "I've come to know the Fanlens team as highly motivated and intelligent individuals. We are currently tasking Fanlens with the R&D of our machine learning features and couldn't be happier!",
              img: "allan",
            },
            {
              name: "Christoph Holz",
              context: "CEO of Visalyze",
              href: "https://visalyze.com",
              comment: "Fanlens ist eine äußerst interessante Firma und Technologie, die es ermöglicht Machine Learning Probleme mittels simplen Plug&Play Komponenten zu lösen.",
              img: "christoph",
            }
          ], (customer, idx) => (
            <Customer key={idx} {... customer}/>
          ))}
        </Endless>
      </Card>
    </div>
  </div>
);

const Sponsor = ({name, context, href, comment, img, imgType = 'jpg'}) => (
  <Card style={{textAlign: 'left', boxShadow: 'none'}}>
    <CardHeader
      title={name}
      subtitle={context}
    />
    <CardMedia mediaStyle={{textAlign: 'center', paddingBottom: '1em'}}>
      <a href={href} target="_blank">
        <img src={`/static/img/${img}-256.${imgType}`} style={{minWidth: '256px', width: '256px'}}/>
      </a>
    </CardMedia>
  </Card>
);

const Sponsors = () => (
  <div className="row top-xs center-xs">
    <div className="col-md-7 col-xs-12">
      <Card style={{textAlign: 'left'}}>
        <CardHeader title="Our Awesome Partners & Sponsors"/>
        <Endless random={true} tight={true}>
          {_.map([
              {
                name: "Land Tirol",
                context: "Innovationsförderung (Public Grant)",
                href: "https://www.tirol.gv.at/arbeit-wirtschaft/wirtschaftsfoerderung/innovationsfoerderung/",
                img: "tirol",
              },
              {
                name: "European Data Science Academy",
                context: "Furthering European Data Science Curricula. Proud Ambassadors.",
                href: "http://edsa-project.eu",
                imgType: 'png',
                img: "edsa",
              },
              {
                name: "Center for Academic Spinoffs (CAST)",
                context: "Incubation and Mentorship Program",
                href: "http://www.cast-tyrol.com",
                imgType: 'png',
                img: "cast",
              }
            ],
            (sponsor, idx) => (
              <Sponsor key={idx} {... sponsor}/>
            ))}
        </Endless>
      </Card>
    </div>
  </div>
);

const TeamPage = () => (
  <main id="team"
        style={{display: 'flex', flexDirection: 'column', flex: '1 1 auto'}}>
    <div style={{overflowY: 'scroll', padding: '16px'}}>
      <h1 style={{textAlign: 'center'}}>
        <a style={{color: 'white', fontWeight: 'bold'}} className="awesome" href="/jobs/cgo" target="_blank">!!! WE ARE HIRING A CGO !!!</a>
      </h1>
      <Team/>
      <Customers/>
      <Sponsors/>
    </div>
  </main >
);

export default TeamPage;
