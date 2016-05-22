//var vide=document.getElementById("com");
//vide.value="";
function writeComment(){
	var regSepURL = new RegExp('/');
	var title=document.URL.split(regSepURL);
	commentaire=document.getElementById("writecomment").value;
	$.get('/write_comment/'+title[4], {key: commentaire}).done(function() {
		var cookie=getCookie();
		var username= cookie["username"];
		var res=document.getElementById("comment");
		res.innerHTML='</br> <div class="commentaire"><a href="/profile/'+username+'"> User '+ username +"</a>:</br>"+document.getElementById("writecomment").value+'</div>'+res.innerHTML
		document.getElementById("writecomment").value="";
	});
}

function getComment(){
	var regSepURL = new RegExp('/');
	var title=document.URL.split(regSepURL);
	$.get('/get_comment/'+title[4]).done(function(data){
		alert(data)
	});
}
getComment();
		