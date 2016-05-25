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
		while (i<res.length){
			if(i%5==0){
				geocoder.geocode( {'address': res[i]+" "+res[i+1]+" "+res[i+2]}, function (i){
				
				return (function(results, status) {
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
									
									content:"<div style=\"text-align:center\"> Imprimante de <a href=\"/profile/"+res[i+3]+"\">"+res[i+3]+"</a> </br>Adresse: "+results[0].formatted_address+"</br> <a href=\"printer/"+res[i+4]+"\">Voir l'annonce </a></div>"
							});

								infowindow.open(map,marker);
							});
						
					}
					else {
						//alert("Le geocodage n\'a pu etre effectue pour la raison suivante: " + status);
					}
					
					}
					
					);
					}(i)
					)
				}
				//alert(res[i])
				//l.push(res[i])
				i++
		}
		//alert(l.length)
		//l=["France","Lama","Kazakhstan","Lyon","Marseille","New-York","Paris","20 Avenue Albert Einstein, 69100 Villeurbanne","6 Avenue des Arts, 69100 Villeurbanne"]
	
	});
	
	
	
	
}
res=[]
i=0;
j=0;
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



geocoder.geocode({'address':address}, function(location, idx){
        return(function(results, status){
            if (status == google.maps.GeocoderStatus.OK) {
                var latlng = results[0].geometry.location;
 
                console.log(location);
                console.log(idx);
            }
        });
    }(location, idx))
