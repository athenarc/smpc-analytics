var cb0 = document.querySelectorAll('input[type="checkbox"]')[0];
var cb1 = document.querySelectorAll('input[type="checkbox"]')[1];
var cb2 = document.querySelectorAll('input[type="checkbox"]')[2];

cb0.addEventListener("click", function () {
    if(cb0.checked){
        document.getElementById("AgeCells").style.display = "inline";
        document.getElementById("AgeCells").value = "3";
    } else {
        document.getElementById("AgeCells").style.display = "none";
        document.getElementById("AgeCells").value = "";
    }
});

cb1.addEventListener("click", function () {
    if(cb1.checked){
        document.getElementById('HeightCells').style.display = "inline";
        document.getElementById('HeightCells').value = "3";
    } else {
        document.getElementById('HeightCells').style.display = "none";
        document.getElementById('HeightCells').value = "";
    }
});

cb2.addEventListener("click", function () {
    if(cb2.checked){
        document.getElementById('WeightCells').style.display = "inline";
        document.getElementById('WeightCells').value = "3";
    } else {
        document.getElementById('WeightCells').style.display = "none";
        document.getElementById('WeightCells').value = "";
    }
});
