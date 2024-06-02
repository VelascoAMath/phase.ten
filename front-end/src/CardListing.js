import React, { useEffect, useState } from "react";

export default function CardListing() {

  const [deck, setDeck] = useState([]);

    useEffect(() => {


      const compareCards = function(a, b){
        const colorOrder = ["red", "blue", "green", "yellow", "wild", "skip"];
        const rankOrder = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "skip", "wild"]

        return (colorOrder.indexOf(a.color) - colorOrder.indexOf(b.color)) || (rankOrder.indexOf(a.rank) - rankOrder.indexOf(b.rank));

      }

      const fetchDeck = async () => {
        try{
          const response = await fetch("http://localhost:8000/cards.json", {
              "headers": {
                  "Content-Type": "application/json",
                  "Accept"      : "application/json",
              },
              "method": "GET",
          })
          const json = await response.json();
          json.sort(compareCards);
          setDeck(json);
        } catch(error){
          console.error(error);
        }
      }

      fetchDeck();

    }, [])

    const getClassFromRank = function(rank) {
      if(rank === 'skip'){
          return 'card skip';
      }
      if(rank === 'wild'){
          return 'card wild';
      }
      return 'card';
  }

    const getDeckDivs = function(){  
      const x = deck.map((card) => {return <div style={{backgroundColor: card.color}} key={card.id} className={getClassFromRank(card.rank)}>{card.rank}</div>} );
      return x;
  }



    return (
        <div className="card-collection">
          {getDeckDivs()}
        </div>
    );
}
