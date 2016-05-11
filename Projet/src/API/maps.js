


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
	
	l=["France","Lama","Kazakhstan","Lyon","Marseille","New-York","Paris","20 Avenue Albert Einstein, 69100 Villeurbanne","6 Avenue des Arts, 69100 Villeurbanne"]
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
							content:"Nicholas = Caca!"
					});

						infowindow.open(map,marker);
				});
			}
			else {
				alert("Le geocodage n\'a pu etre effectue pour la raison suivante: " + status);
			}
		});
		
		
	}
	
}

google.maps.event.addDomListener(window, 'load', initialize);
if(navigator.geolocation) {
	  
	  navigator.geolocation.getCurrentPosition(successCallback,errorCallback,{timeout:10000});

	} else {
	 alert("Merde !");
	}
	
function successCallback(position){
		alert("test");
		var center = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
		// using global variable:
		map.panTo(center);
		map.setZoom(13);
}

function errorCallback(msg){
		aert("connard");
}
