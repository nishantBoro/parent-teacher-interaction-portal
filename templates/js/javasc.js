function myfunction(){
    var x=document.getElementById('one').value
    var y=document.getElementById('two').value


  if(x=="" || y==""){
    alert("Both passwords must be entered");
  window.location="reg.php";
  }

  else if(x==y) {
    alert("Correct password entered on both fields!");
    return true;
  }
    else {
      alert("The passwords must match!");
      window.location="reg.php";
}
}