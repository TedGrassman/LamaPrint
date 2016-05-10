function  getCookie(){
	button=document.getElementById("connectionButton");
    alert(document.cookie.length);
	 /*
     var regSepCookie = new RegExp('(; )', 'g');
     var cookies = document.cookie.split(regSepCookie);

     for(var i = 0; i < cookies.length; i++){
       var regInfo = new RegExp('=', 'g');
       var infos = cookies[i].split(regInfo);
	   for (i=0; i<infos.length; i++){
		   if(infos[i] == username){
			  button.style.color="red"
		   }
	   }
     }
     return null;*/
}
/*function getCookie(sName) {
        var oRegex = new RegExp("(?:; )?" + sName + "=([^;]*);?");
        if (oRegex.test(document.cookie)) {
                return decodeURIComponent(RegExp["$1"]);
        } else {
                return null;
        }
}*/

function createCookie(sName,sValue){
        //expires.setTime(today.getTime() + (10*60*1000));//10 minutes avant expiration
        document.cookie = sName + "=" + encodeURIComponent(sValue);
		alert("Creation cookie:"+sName+"="+sValue);
}

function connexion(){
	var value = document.getElementById("test").value;
	createCookie("ID", value);
}
