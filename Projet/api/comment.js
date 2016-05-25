//var vide=document.getElementById("com");
//vide.value="";
function writeComment(){
	var regSepURL = new RegExp('/');
	var title=document.getElementById("title").innerHTML;
	commentaire=document.getElementById("writecomment").value;
	$.get('/write_comment/'+title, {key: commentaire}).done(function() {
		var cookie=getCookie();
		var username= cookie["username"];
		var res=document.getElementById("comment");
		res.innerHTML='</br> <div class="commentaire"><a href="/profile/'+username+'"> User '+ username +"</a>:</br>"+document.getElementById("writecomment").value+'</div>'+res.innerHTML
		document.getElementById("writecomment").value="";
	});
}

function getComment(){
	var regSepURL = new RegExp('/');
	var title=document.getElementById("title").innerHTML;
	$.get('/get_comment/'+title).done(function(data){
		alert(data)
	});
}
getComment();
		