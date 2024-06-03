
const callPOST = (url, body) => {

  let returnedData = null;
  fetch(url, {
    "headers": {
      "Content-Type": "application/json",
      "Accept"      : "application/json",
    },
    "body": JSON.stringify(body),
    "method": "POST",
  })
  .then(res => {
  if (!res.ok) { // error coming back from server
      throw Error('could not fetch the data for that resource');
  } 
  return res.json();
  })
  .then(data => {
      returnedData = data;
  })
  .catch(err => {
    alert("ERROR: " + err);
  })

  return returnedData;
}
 
export default callPOST;