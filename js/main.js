function toggle() {
	var ele = document.getElementById("register");
	var text = document.getElementById("registerForm");
	if(ele.style.display == "block") {
    		ele.style.display = "none";
		text.innerHTML = "Register";
  	}
	else {
		ele.style.display = "block";
		text.innerHTML = "Register";
	}
}