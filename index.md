<div id="inner_wrapper">
        <h5 id="ideology-result" style="text-align:center"></h5>
        <p id="description-result" style="text-align:left;white-space:pre-line"></p>
    <div id="button-div">
        <button type="button" class="btn btn-danger" id="generate-result" onclick="generateNew(); ga('send', 'event', 'MainButton', 'Click');">MORE</button>
        <button type="button" class="btn btn-success" id="generate-description" onclick="generateDescription(); ga('send', 'event', 'DescriptionButton', 'Click');">DESCRIBE</button>
    </div>
</div>

<div class="fb-share-button" data-href="https://danielpbak.github.io/IdeologyGenerator/" data-layout="button" data-size="small" style="position:fixed; bottom:10px; right:10px;"><a target="_blank" onclick="CaptureFacebookShare(); return false;" href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fdanielpbak.github.io%2FIdeologyGenerator%2F&amp;src=sdkpreparse" class="fb-xfbml-parse-ignore">Share</a></div>

<link href="https://stackpath.bootstrapcdn.com/bootswatch/4.4.1/cyborg/bootstrap.min.css" rel="stylesheet" integrity="sha384-l7xaoY0cJM4h9xh1RfazbgJVUZvdtyLWPueWNtLAphf/UbBgOVzqbOTogxPwYLHM" crossorigin="anonymous">

<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>


<script>
const Http = new XMLHttpRequest();
const url='https://975kxs927c.execute-api.us-east-1.amazonaws.com/Prod/service_ideology/Prod';
let ideologies = [];
let description = "";
let generating_description = false;
let description_generated = false;

Http.onreadystatechange = (e) => {
  if(Http.readyState === XMLHttpRequest.DONE) {
      let this_response = JSON.parse(Http.responseText);
      let mode = this_response['mode'];
  
      if (mode === "ideologies"){
        ideologies = ideologies.concat(this_response['ideologies']);
        if (document.getElementById("ideology-result").innerHTML === ""){
          let new_ideo = ideologies.shift();
          description = "";
          document.getElementById("ideology-result").innerHTML = new_ideo;
          window.history.replaceState(null, null, "?ideology=" + new_ideo);
        }
      }
        else if (mode === "description"){
            description = this_response['description'];
            document.getElementById("description-result").innerHTML = description;
            document.getElementById("generate-description").innerHTML = "DESCRIBED!";
            description_generated = true;

            generating_description = false;
        }
  }
}

function generateFromURL(){
  urlParams = new URLSearchParams(window.location.search);
  ideology = urlParams.get('ideology');
  
  if (!ideology){
    return false;
  }
  
  document.getElementById("ideology-result").innerHTML = ideology;
  
  return true;
  
  
}

function generateDescription(){

    if (generating_description || description_generated){
        return;
    }
    let ideology = document.getElementById("ideology-result").innerHTML;
    let to_send = {mode: "description", ideology_to_describe: ideology, narrator: "academic"};
    document.getElementById("generate-description").innerHTML = "DESCRIBING...";
    generating_description = true;

      if (ga.getAll().length && ga.getAll()[0].get('clientId')){
        to_send['g_client_id'] = ga.getAll()[0].get('clientId');
      }

    Http.open("POST", url);
    Http.send(JSON.stringify(to_send));
}

function generateNew(){

    if (generating_description){
        return;
    }

    description_generated = false;
    document.getElementById("generate-description").innerHTML = "DESCRIBE";

    description = "";
  document.getElementById("description-result").innerHTML = description;

  if (ideologies.length > 0){
        new_ideo = ideologies.shift();
        document.getElementById("ideology-result").innerHTML = new_ideo;
        window.history.replaceState(null, null, "?ideology=" + new_ideo);
  }
  let to_send = {mode: "ideologies"};

  if (ideologies.length <= 1){
    to_send['n_ideo'] = 15;
    Http.open("POST", url);
    Http.send(JSON.stringify(to_send));
  }
  else if (ideologies.length <= 5){
      Http.open("POST", url);
      if (ga.getAll().length && ga.getAll()[0].get('clientId')){
        to_send['g_client_id'] = ga.getAll()[0].get('clientId');
      }
      to_send['n_ideo'] = 25;
      Http.send(JSON.stringify(to_send));
  }
    
 }
 
var CaptureOutboundLink = function(url) {
   ga('send', 'event', 'outbound', 'click', url, {
     'transport': 'beacon',
     'hitCallback': function(){document.location = url;}
   });
}

var CaptureFacebookShare = function() {
   ga('send', 'event', 'share', 'click',  {
     'transport': 'beacon',
     'hitCallback': function(){}
   });
}

generateNew();
generateFromURL();
 
 
</script>

