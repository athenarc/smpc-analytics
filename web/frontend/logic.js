var checkboxes = document.querySelectorAll('input[type="checkbox"]');
var cells = document.querySelectorAll('input[type="number"]');

for (var i = 0; i < checkboxes.length; i++) {
    var closureMaker = function(i) {
        return function(event){
            if(checkboxes[i].checked){
                cells[i].style.display = "inline";
                cells[i].value = "3";
                cells[i].required = "true";
            } else {
                cells[i].style.display = "none";
                cells[i].required = "false";
                cells[i].value = "";
            }
        };
    };
    var closure = closureMaker( i );
    checkboxes[i].addEventListener('click', closure, false);
}