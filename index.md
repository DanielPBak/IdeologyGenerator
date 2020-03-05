<div id="ideology-result"></div>
 
<script>
 
const Http = new XMLHttpRequest();
const url='https://cors.io/?https://975kxs927c.execute-api.us-east-1.amazonaws.com/default/service_ideology';
Http.open("GET", url);
Http.send();

Http.onreadystatechange = (e) => {
  document.getElementById("ideology-result").innerHTML = Http.responseText;
}
 
</script>
