import './css/tagger.css'

import 'babel-polyfill'
import React from 'react';
import {render} from 'react-dom';
import {createStore, combineReducers, applyMiddleware} from 'redux'
import {Provider} from 'react-redux'
import createLogger from 'redux-logger'
import thunkMiddleware from 'redux-thunk'
import _ from 'lodash'

import {fetchSources, fetchRandomComments, fetchStats} from './actions/TaggerActions'
import alerts from './reducers/alerts'
import tagger from './reducers/tagger'

import TaggerApp from './components/TaggerApp.jsx'
import AlertsApp from './components/AlertsApp.jsx'

const taggerReducers = combineReducers({
  alerts,
  tagger
});

const store = createStore(
  taggerReducers,
  applyMiddleware(
    thunkMiddleware,
    createLogger()
  )
)
render(
  <Provider store={store}>
    <TaggerApp count={5}/>
  </Provider>,
  document.getElementById('app')
);
render(
  <Provider store={store}>
    <AlertsApp />
  </Provider>,
  document.getElementById('alerts')
);

//TODO wtf? refactor!
store.dispatch(fetchSources())
  .then(_.chain(store.getState().tagger.sources).filter('active').map('id').each(source => {
    store.dispatch(fetchStats(source))
  }).value())
  .then(store.dispatch(fetchRandomComments(5, _.chain(store.getState().tagger.sources).filter('active').map('id').value())));
