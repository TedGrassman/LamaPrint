function getSession(){
	alert("infct");
	var session;
	$.ajaxSetup({cache: false})
	$.get('/login', function (data) {
		session = data;
	});
	alert(session);
}

