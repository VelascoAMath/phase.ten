import React, { Component } from 'react';
import CardCreation from './CardCreation';
import CardListing from './CardListing.js';
import Home from './Home.js';

import PlayerListing from './PlayerListing';
import PlayerCreation from './PlayerCreation'
import PlayerPage from './PlayerPage';
import GameRoom from './GameRoom';
import { Link, Route } from "wouter";

class App extends Component {
  render() {
    return (
      <div>
        <Route path="/cards">
          <CardCreation/>
          <CardListing/>
        </Route>
        <Route path="/player/:id" component={PlayerPage} ></Route>
        <Route path="/players">
          <PlayerCreation></PlayerCreation>
          <PlayerListing></PlayerListing>
        </Route>
        <Route path="/games">
          <GameRoom></GameRoom>
        </Route>
        <Route path="/" component={Home} ></Route>
      </div>

    );
  }
}

export default App;
