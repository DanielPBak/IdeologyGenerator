<div id="inner_wrapper">
  <h5 id="ideology-result" style="text-align:center"></h5>
  <div id="button-div">
    <button type="button" class="btn btn-danger" id="generate-result" onclick="generateNew()">MORE</button>
  </div>
</div>

<div class="fb-share-button" data-href="https://danielpbak.github.io/IdeologyGenerator/" data-layout="button" data-size="small" style="position:fixed; bottom:10px; right:10px;"><a target="_blank" href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fdanielpbak.github.io%2FIdeologyGenerator%2F&amp;src=sdkpreparse" class="fb-xfbml-parse-ignore">Share</a></div>

<link href="https://stackpath.bootstrapcdn.com/bootswatch/4.4.1/cyborg/bootstrap.min.css" rel="stylesheet" integrity="sha384-l7xaoY0cJM4h9xh1RfazbgJVUZvdtyLWPueWNtLAphf/UbBgOVzqbOTogxPwYLHM" crossorigin="anonymous">

<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>


<script>
const Http = new XMLHttpRequest();
const url='https://975kxs927c.execute-api.us-east-1.amazonaws.com/Prod/service_ideology/Prod';
var ideologies = [];

Http.onreadystatechange = (e) => {
  if(Http.readyState === XMLHttpRequest.DONE) {
      ideologies = ideologies.concat(JSON.parse(Http.responseText));
      if (document.getElementById("ideology-result").innerHTML == ""){
        document.getElementById("ideology-result").innerHTML = ideologies.shift();
      }
  }
}

function generateNew(){
  if (ideologies.length > 0){
    document.getElementById("ideology-result").innerHTML = ideologies.shift();
  }

  if (ideologies.length <= 1){
    Http.open("GET", url);
    Http.send('15');
  }
  else if (ideologies.length <= 5){
      Http.open("POST", url);
      Http.send('50');
  }
    
 }
 generateNew();
 
 
</script>
