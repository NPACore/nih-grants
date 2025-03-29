// ==UserScript==
// @name        New script nih.gov
// @namespace   Violentmonkey Scripts
// @match       https://reporter.nih.gov/project-details/*
// @grant       GM_xmlhttpRequest
// @version     1.0
// @author      -
// @description 3/29/2025, 3:39:05 PM
// ==/UserScript==

//EMAILS = []
function click_email(){
  b = [ ...document.querySelectorAll("button.project-button")].filter(x=>x.innerText=="View Email")[0];
  console.log(`found button ${b}`)
  b.click();
  //console.log("waiting 2s to find href")
  //setTimeout(read_email, 2000);
}

// no longer used
function read_email() {
  console.log("looking for links")
  a = [...document.querySelectorAll("a")].filter(x=> /@/.test(x.innerHTML))[0];
  console.log(`found link ${a}`)
  //a.scrollIntoView()
  //EMAILS.push({"url": window.location, "email": a.href});
  alert(a.href);
}

// looking at all requests, watching for emails
// inspect every fetched URL to see if it requested emails
function check_request(){
  if(/PiPoEmails/.test(this.responseURL)){
    console.log(this)
    save_email(this.response)
  }
}

// send email json to db server. get next profile id and go to there
function save_email(json_email){
  GM_xmlhttpRequest({
  method: "POST",
  url: "http://www.xn--4-cmb.com/c/collect_nih_email.pl",
  data: json_email,
  headers: {
    "Content-Type": "application/x-www-form-urlencoded"
  },
  onload: function(response) {
    console.log(`got message DB server: ${response.responesText}`);
    if(/^http/.test(response.responseText)){
      waittime = 2000;
      console.log(`matches next profile. waiting ${waittime}ms and then going to next profile.`)
      setTimeout(function() {
        console.log(`going to ${response.responseText}`);
        location.assign(response.responseText);
      }, waittime);
    }
  }
});
}

//Monkey patch all on page requests to also pass through `check_request`
(function(open) {
    XMLHttpRequest.prototype.open = function() {
        this.addEventListener("readystatechange",check_request);
        open.apply(this, arguments);
    };
})(XMLHttpRequest.prototype.open);

// start everything off .5s after page load by finding and clicking the email button
window.addEventListener('load', function() { setTimeout(click_email, 500); })
