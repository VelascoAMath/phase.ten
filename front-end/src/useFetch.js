// https://github.com/iamshaunjp/Complete-React-Tutorial/blob/lesson-20/dojo-blog/src/useFetch.js
import { useState, useEffect } from 'react';

const useFetch = (url) => {
  const [data, setData] = useState(null);
  const [isPending, setIsPending] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(url, {
        "headers": {
        "Content-Type": "application/json",
        "Accept"      : "application/json",
      },
      "method": "GET",
    })
    .then(res => {
      if (!res.ok) { // error coming back from server
        throw Error('could not fetch the data for that resource');

      }
      return res.json();
    })
    .then(data => {
      setIsPending(false);
      setData(data);
      setError(null);
    })
    .catch(err => {
      // auto catches network / connection error
      setIsPending(false);
      setError(err.message);
    })
  }, [url])

  return [ data, isPending, error];
}
 
export default useFetch;