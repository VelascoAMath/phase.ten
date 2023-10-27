import React from 'react';
import { Link } from 'react-router-dom/cjs/react-router-dom.min';


export default function Hello() {
    


    return (
        <div>
            Hello
            <div>
            <Link to="/cards">Play with cards</Link>
            </div>
        </div>
    )
}