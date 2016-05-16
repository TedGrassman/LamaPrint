function  getCookie(){
	 var res= {};
     var regSepCookie = new RegExp(';');
     var cookies = document.cookie.split(regSepCookie);
     for(var i = 0; i < cookies.length; i++){
       var regInfo = new RegExp('=');
       var infos = cookies[i].split(regInfo);
	   //alert(infos[0]);
	   res[infos[0]]=infos[1];
	}
     return res;
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


