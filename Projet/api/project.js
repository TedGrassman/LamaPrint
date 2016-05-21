function showText(clickedID)
{	
	element = document.getElementById("text"+clickedID);
	if(element.className=="hide"){
		element.className="show";
	}
	else{
		element.className="hide";
	}
}


