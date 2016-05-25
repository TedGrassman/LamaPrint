function initialize() {
	
	//myCenter=new google.maps.LatLng(p.coords.latitude,p.coords.longitude));
	myCenter=new google.maps.LatLng(46.227638,2.213749000000007);
	var infowindow = null;
	geocoder = new google.maps.Geocoder();
	
	//GOOGLE MAP
	var mapProp = {
		center:myCenter,
		zoom:5,
		mapTypeId:google.maps.MapTypeId.ROADMAP
	};
	
	map=new google.maps.Map(document.getElementById("googleMap"),mapProp);
	
	
	$.get('/get_printer').done(function(data) {
		//alert(data)
		res=jQuery.parseJSON(data)
		l=[]
		//alert(res[3])
		for(i=0; i<res.length; i++){
			if(i%2==0){
				alert(res[i])
				l.push(res[i])
			}
		}
		alert(l.length)
		//l=["France","Lama","Kazakhstan","Lyon","Marseille","New-York","Paris","20 Avenue Albert Einstein, 69100 Villeurbanne","6 Avenue des Arts, 69100 Villeurbanne"]
		for(i=0; i<l.length; i++){
		geocoder.geocode( {'address': l[i]}, function(results, status) {
		
			if (status == google.maps.GeocoderStatus.OK) {
				/* Affichage du marker */
				var marker = new google.maps.Marker({
					map: map,
					position: results[0].geometry.location
				});
				
				marker.addListener('click', function() {
					if (infowindow) {
						infowindow.close();
					}
					infowindow = new google.maps.InfoWindow({
							content:results[0]
					});

						infowindow.open(map,marker);
				});
			}
			else {
				alert("Le geocodage n\'a pu etre effectue pour la raison suivante: " + status);
			}
		});
		
		
	}
	});
	
	
	
	
}

google.maps.event.addDomListener(window, 'load', initialize);

if(navigator.geolocation) {
	  
	  navigator.geolocation.getCurrentPosition(successCallback,errorCallback,{timeout:10000});

	} else {
	 alert("Geolocation is not activated!");
	}
	
function successCallback(position){
		var center = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
		// using global variable:
		map.panTo(center);
		map.setZoom(13);
}

function errorCallback(msg){
		alert("Error");
}
