 <script type="text/javascript">
        function validateForm(){
            var one=document.getElementById('one').value
            var two=document.getElementById('two').value

            if(one==two){
                alert("Your Information is Correct");
            }
            else{
                alert("Please enter correct password");
                return false;
            }
        }
        function validateField(){
            var x=document.forms["studentreg"]["fname"].value;
            if (x==null || x==""){
            alert("Please enter your name");
            return false;
            }
        }
        </script>





        onsubmit="validateField()" onsubmit="return validateForm(this)"