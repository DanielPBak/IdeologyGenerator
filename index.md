<div id="main">
<div id="ideology-result"></div>
<button type="button" class="btn btn-primary" id="generate-result" onclick="generateNew()">MORE</button>
</div>
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>


<script>
const Http = new XMLHttpRequest();
const url='https://975kxs927c.execute-api.us-east-1.amazonaws.com/default/service_ideology';

Http.onreadystatechange = (e) => {
  if(Http.readyState === XMLHttpRequest.DONE) {
      document.getElementById("ideology-result").innerHTML = Http.responseText;
  }
}

function generateNew(){
    Http.open("GET", url);
    Http.send();

 }
 generateNew();
 
 
</script>