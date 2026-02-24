<div id="inner_wrapper">
        <h5 id="ideology-result" style="text-align:center"></h5>
    <div id="button-div">
        <button type="button" class="btn btn-danger" id="generate-result" onclick="generateNew();">MORE</button>
    </div>
</div>

<div class="fb-share-button" data-href="https://danielpbak.github.io/IdeologyGenerator/" data-layout="button" data-size="small" style="position:fixed; bottom:10px; right:10px;"><a target="_blank" onclick="CaptureFacebookShare(); return false;" href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fdanielpbak.github.io%2FIdeologyGenerator%2F&amp;src=sdkpreparse" class="fb-xfbml-parse-ignore">Share</a></div>

<link href="https://stackpath.bootstrapcdn.com/bootswatch/4.4.1/cyborg/bootstrap.min.css" rel="stylesheet" integrity="sha384-l7xaoY0cJM4h9xh1RfazbgJVUZvdtyLWPueWNtLAphf/UbBgOVzqbOTogxPwYLHM" crossorigin="anonymous">

<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>


<script>
var CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1woWAU1ClzNJBUElMoxLstPYmhq0JfdajTjBABMM3TqpLE5wevkO6SHeoz2a6NS0pDielm9Zx2bWB/pub?gid=0&single=true&output=csv";

// ── CSV parser ──────────────────────────────────────────────────────
// Handles quoted fields (which may contain commas and newlines).
function parseCSV(text) {
  var rows = [];
  var row = [];
  var field = "";
  var inQuotes = false;
  var i = 0;
  while (i < text.length) {
    var ch = text[i];
    if (inQuotes) {
      if (ch === '"') {
        if (i + 1 < text.length && text[i + 1] === '"') {
          field += '"';
          i += 2;
        } else {
          inQuotes = false;
          i++;
        }
      } else {
        field += ch;
        i++;
      }
    } else {
      if (ch === '"') {
        inQuotes = true;
        i++;
      } else if (ch === ',') {
        row.push(field);
        field = "";
        i++;
      } else if (ch === '\r') {
        if (i + 1 < text.length && text[i + 1] === '\n') {
          i++;
        }
        row.push(field);
        field = "";
        rows.push(row);
        row = [];
        i++;
      } else if (ch === '\n') {
        row.push(field);
        field = "";
        rows.push(row);
        row = [];
        i++;
      } else {
        field += ch;
        i++;
      }
    }
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

// ── Title-case helper (matches Python str.title() behavior) ─────────
// Python's title() capitalizes the character after any non-alpha character.
function titleCase(s) {
  var result = "";
  var capitalizeNext = true;
  for (var i = 0; i < s.length; i++) {
    var ch = s[i];
    if (/[a-zA-Z]/.test(ch)) {
      result += capitalizeNext ? ch.toUpperCase() : ch.toLowerCase();
      capitalizeNext = false;
    } else {
      result += ch;
      capitalizeNext = true;
    }
  }
  return result;
}

// ── Generator class ─────────────────────────────────────────────────
function Generator(csvText) {
  this.descAdjs = [];
  this.descAdjsWeights = [];
  this.descAdjsHaspWeights = [];
  this.descNouns = [];
  this.descNounsWeights = [];
  this.descNounsHaspWeights = [];
  this.prefixes = [];
  this.prefixWeights = [];
  this.prefixHaspWeights = [];
  this.nouns = [];
  this.nounsWeights = [];
  this.nounsHaspWeights = [];
  this.adverbs = [];
  this.adverbsWeights = [];
  this.endings = [];
  this.endingsWeights = [];

  this.allDescs = [];
  this.allDescsWeights = [];
  this.allDescsHaspWeights = [];

  this.trace = [];
  this.csvText = csvText;
}

Generator.prototype.getWords = function () {
  var rows = parseCSV(this.csvText);
  var first = true;

  for (var r = 0; r < rows.length; r++) {
    var row = rows[r];
    if (first) { first = false; continue; }
    if (row.length < 4) continue;
    if (row[0] === "") continue;

    var rawWords = row[0];
    var wordList = rawWords.split(",");
    wordList = wordList.map(function (w) {
      var cleaned = w.replace(/;/g, ",");
      cleaned = cleaned.replace(/'/g, "abcdefgh");
      cleaned = titleCase(cleaned);
      cleaned = cleaned.replace(/abcdefgh/g, "'");
      return cleaned;
    });

    var type = row[1];
    var weight = row[2] === "" ? 1 : parseFloat(row[2]);
    var haspWeight = row[3] === "" ? 1 : parseFloat(row[3]);

    if (type === "DESCADJ") {
      this.descAdjs.push(wordList);
      this.descAdjsWeights.push(weight);
      this.descAdjsHaspWeights.push(haspWeight);
    } else if (type === "DESCNOUN") {
      this.descNouns.push(wordList);
      this.descNounsWeights.push(weight);
      this.descNounsHaspWeights.push(haspWeight);
    } else if (type === "PREFIX") {
      this.prefixes.push(wordList);
      this.prefixWeights.push(weight);
      this.prefixHaspWeights.push(haspWeight);
    } else if (type === "ENDING") {
      this.endings.push(wordList);
      this.endingsWeights.push(weight);
    } else if (type === "NOUN") {
      this.nouns.push(wordList);
      this.nounsWeights.push(weight);
      this.nounsHaspWeights.push(haspWeight);
    } else if (type === "ADVERB") {
      this.adverbs.push(wordList);
      this.adverbsWeights.push(weight);
    }
  }

  this.allDescs = this.descAdjs.concat(this.descNouns);
  this.allDescsWeights = this.descAdjsWeights.concat(this.descNounsWeights);
  this.allDescsHaspWeights = this.descAdjsHaspWeights.concat(this.descNounsHaspWeights);
};

Generator.prototype.weightedChoice = function (weights) {
  var totals = [];
  var runningTotal = 0;
  for (var i = 0; i < weights.length; i++) {
    runningTotal += weights[i];
    totals.push(runningTotal);
  }
  var rnd = Math.random() * runningTotal;
  for (var i = 0; i < totals.length; i++) {
    if (rnd < totals[i]) return i;
  }
  return weights.length - 1;
};

Generator.prototype.randomChoice = function (arr) {
  return arr[Math.floor(Math.random() * arr.length)];
};

Generator.prototype.getNoun = function (pAdj, pPrefix, pDouble, isDouble) {
  if (pAdj === undefined) pAdj = 0.5;
  if (pPrefix === undefined) pPrefix = 0.5;
  if (pDouble === undefined) pDouble = 0.25;
  if (isDouble === undefined) isDouble = false;

  this.trace.push("Noun");
  var noun = this.randomChoice(this.nouns[this.weightedChoice(this.nounsWeights)]);

  var hasDouble = Math.random() < pDouble;

  if (hasDouble) {
    pPrefix = pPrefix / 2;
    pAdj = pAdj / 2;
  }

  var hasPrefix = Math.random() < pPrefix;
  var hasAdj = Math.random() < pAdj;
  var newPPrefix = Math.min(pPrefix * pPrefix, pPrefix * 0.25);
  var newPAdj = Math.min(pAdj * pAdj, pAdj * 0.25);

  if (hasPrefix) {
    var prefixPHyphen = isDouble ? 0 : 0.25;
    var prefix = this.getPrefix(newPPrefix, prefixPHyphen);
    noun = prefix + noun;
  }

  if (hasAdj) {
    noun = this.getDesc(newPAdj, newPPrefix) + " " + noun;
  }

  if (hasDouble) {
    noun = noun + "-" + this.getNoun(0, 0.25, 0, true);
  }

  return noun;
};

Generator.prototype.getDesc = function (pPrefix, pAdj, pDouble, pAdverb) {
  if (pPrefix === undefined) pPrefix = 0.5;
  if (pAdj === undefined) pAdj = 0.33;
  if (pDouble === undefined) pDouble = 0.4;
  if (pAdverb === undefined) pAdverb = 0.2;

  var newPPrefix = Math.min(pPrefix * pPrefix, pPrefix * 0.33);
  var newPAdj = Math.min(pAdj * pAdj, pAdj * 0.33);

  this.trace.push("Desc");
  var descIdx = this.weightedChoice(this.allDescsWeights);
  var adjs = this.allDescs[descIdx];

  var addAdverb = false;
  var isDescAdj = descIdx < this.descAdjs.length;

  if (isDescAdj && Math.random() < pAdverb) {
    addAdverb = true;
  }

  var adj = this.randomChoice(adjs);
  var prefixWeight = this.allDescsHaspWeights[descIdx];

  adj = adj.replace(/\{Adj1\}/g, "{adj1}");
  adj = adj.replace(/\{Adj2\}/g, "{adj2}");
  adj = adj.replace(/\{Adj\}/g, "{adj}");
  adj = adj.replace(/\{Noun\}/g, "{noun}");

  if (adj.indexOf("{adj1}") !== -1 || adj.indexOf("{adj2}") !== -1) {
    var adj1Val = this.getDesc(newPPrefix, newPAdj, 0);
    var adj2Val = this.getDesc(newPPrefix, newPAdj, 0);
    adj = adj.replace(/\{adj1\}/g, adj1Val).replace(/\{adj2\}/g, adj2Val);
    return adj;
  }

  if (isDescAdj && Math.random() < pDouble) {
    adj = adj + "-" + this.getDesc(0.1, 0, 0, 0);
  }

  if (Math.random() < pPrefix * prefixWeight) {
    adj = this.getPrefix(newPPrefix) + adj;
  }

  if (addAdverb) {
    adj = this.getAdverb() + " " + adj;
  }

  if (Math.random() < pAdj) {
    adj = this.getDesc(newPPrefix, newPAdj) + " " + adj;
  }

  return adj;
};

Generator.prototype.getPrefix = function (pPrefix, pHyphen) {
  if (pPrefix === undefined) pPrefix = 0.15;
  if (pHyphen === undefined) pHyphen = 0.5;

  this.trace.push("prefix");
  var newPPrefix = Math.min(pPrefix * pPrefix, pPrefix * 0.33);

  var prefixIdx = this.weightedChoice(this.prefixWeights);
  var prefixWeight = this.prefixHaspWeights[prefixIdx];

  var pref = this.randomChoice(this.prefixes[prefixIdx]);

  var pNextHyphen;
  if (pref.endsWith("-")) {
    pNextHyphen = 1;
  } else {
    if (Math.random() < pHyphen) {
      pref = pref + "-";
      pNextHyphen = pHyphen;
    } else {
      pNextHyphen = 1;
    }
  }

  if (Math.random() < pPrefix * prefixWeight) {
    pref = this.getPrefix(newPPrefix, pNextHyphen) + pref;
  }

  return pref;
};

Generator.prototype.getEnding = function () {
  this.trace.push("ending");
  var ending = this.randomChoice(this.endings[this.weightedChoice(this.endingsWeights)]);

  ending = ending.replace(/\{Adj\}/g, "{adj}");
  ending = ending.replace(/\{Noun\}/g, "{noun}");

  var desc = this.getDesc(0.2, 0.1, 0.2);
  var noun = this.getNoun(0.1, 0.2, 0.2);

  ending = ending.replace(/\{adj\}/g, desc).replace(/\{noun\}/g, noun);

  return ending;
};

Generator.prototype.getAdverb = function () {
  this.trace.push("adverb");
  return this.randomChoice(this.adverbs[this.weightedChoice(this.adverbsWeights)]);
};

Generator.prototype.generateIdeology = function (pEnding, pStart) {
  if (pEnding === undefined) pEnding = 0.33;
  if (pStart === undefined) pStart = 0.5;

  var forcePrefix = this.randomChoice([false, true]);
  var withEnding = Math.random() < pEnding;

  var pPrefix, pAdj;
  if (forcePrefix) {
    pPrefix = 1;
    pAdj = 0.75;
  } else {
    pPrefix = 0.75;
    pAdj = 1;
  }

  var noun = this.getNoun(pPrefix, pAdj);
  var ideo = noun;

  if (withEnding) {
    var ending = this.getEnding().trim();
    if (ending.charAt(0) === ",") {
      ideo = ideo + ending;
    } else {
      ideo = ideo + " " + ending;
    }
  }

  return ideo;
};

// ── Application logic ───────────────────────────────────────────────
var generator = null;

function generateFromURL() {
  var urlParams = new URLSearchParams(window.location.search);
  var ideology = urlParams.get("ideology");
  if (!ideology) return false;
  document.getElementById("ideology-result").innerHTML = ideology;
  return true;
}

function generateNew() {
  if (!generator) return;
  generator.trace = [];
  var ideo = generator.generateIdeology();
  document.getElementById("ideology-result").innerHTML = ideo;
  window.history.replaceState(null, null, "?ideology=" + encodeURIComponent(ideo));
}

var CaptureFacebookShare = function() {
  if (typeof ga !== "undefined") {
    ga('send', 'event', 'share', 'click', {
      'transport': 'beacon',
      'hitCallback': function(){}
    });
  }
}

function init() {
  var hadURLIdeology = generateFromURL();

  fetch(CSV_URL)
    .then(function (response) { return response.text(); })
    .then(function (csvText) {
      generator = new Generator(csvText);
      generator.getWords();
      if (!hadURLIdeology) {
        generateNew();
      }
    })
    .catch(function (err) {
      console.error("Failed to load word list:", err);
      document.getElementById("ideology-result").innerHTML = "Failed to load word list.";
    });
}

init();
</script>

