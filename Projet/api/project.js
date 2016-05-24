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

i=0;
$("#addbutton").on('click', function()
	{ 
	element =document.getElementById("filebuttons");
	element.innerHTML=element.innerHTML+"<p><input type=\"file\" name=\"fichier"+i+"\" id=\"fichier"+i+"\" style=\"margin-left:25px\" required/>"
	}
);