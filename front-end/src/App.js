import React, { Component } from 'react';
import CardCreation from './CardCreation';
import CardListing from './CardListing.js';
import Home from './Home.js';

import PlayerListing from './PlayerListing';
import PlayerCreation from './PlayerCreation'
import PlayerPage from './PlayerPage';
import GameRoom from './GameRoom';
import { Route } from "wouter";
import GamePlay from './GamePlay.js';

class App extends Component {


  render() {
    
    return (
      <div>
        <Route path="/cards">
          <CardCreation/>
          <CardListing/>
        </Route>
        <Route path="/signup" component={PlayerCreation}></Route>
        <Route path="/login" component={PlayerCreation}></Route>
        <Route path="/player/:id" component={PlayerPage} ></Route>
        <Route path="/players">
          <PlayerListing></PlayerListing>
        </Route>
        <Route path="/test_game" component={GamePlay}/>
        <Route path="/games">
          <GameRoom></GameRoom>
        </Route>
        <Route path="/" component={Home} ></Route>
      </div>

    );
  }
}

export default App;
