function test(){
	var cookie=getCookie();
	var username= cookie["username"];
	var com=document.getElementById("com");
	var res=document.getElementById("older-comments");
	res.innerHTML=res.innerHTML+'</br> <div class="commentaire"><a href="/profile/'+username+'">'+ username +"</a>: "+com.value+'</div>';
	com.value="";
}

var vide=document.getElementById("com");
vide.value="";
