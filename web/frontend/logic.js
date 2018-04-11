$(document).ready(function(){
$('#btnAdd').click(function (e) {
    	var nextTab = $('#tabs li').length+1;

    	// create the tab
    	$('<li class="nav-item"><a class="nav-link" href="#tab'+nextTab+'" id="tab'+nextTab+'-tab" data-toggle="tab">Histogram '+nextTab+'</a></li>').appendTo('#tabs');

    	// create the tab content
    	$('<div class="tab-pane fade" id="tab'+nextTab+'">'+`  <form action="/histogram" method="post" id="hist_`+nextTab+`">
          <p>
            <ul class="list-group">
                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="Patient Age"> Patient Age &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="Heart rate"> Heart rate &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="Height (cm)"> Height (cm) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="Weight (kg)"> Weight (kg) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="LVEDV (ml)"> LVEDV (ml) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="LVESV (ml)"> LVESV (ml) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="LVSV (ml)"> LVSV (ml) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="LVEF (%)"> LVEF (%) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="LV Mass (g)"> LV Mass (g) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="RVEDV (ml)"> RVEDV (ml) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="RVESV (ml)"> RVESV (ml) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="RVSV (ml)"> RVSV (ml) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="RVEF (%)"> RVEF (%) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="RV Mass (g)"> RV Mass (g) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="BMI (kg/msq)"> BMI (kg/msq) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="BSA"> BSA &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="BSA (msq)"> BSA (msq) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="CO (L/min)"> CO (L/min) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="Central PP(mmHg)"> Central PP(mmHg) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="DBP (mmHg)"> DBP (mmHg) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="LVEF (ratio)"> LVEF (ratio) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="MAP"> MAP &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="PAP (mmHg)"> PAP (mmHg) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="PP (mmHg)"> PP (mmHg) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="RVEF (ratio)"> RVEF (ratio) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="SBP (mmHg)"> SBP (mmHg) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

                <li class="list-group-item">
                  <input type="checkbox" name="attributes" value="SVR (mmHg/L/min)"> SVR (mmHg/L/min) &ensp;
                  <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" class="answer_list" placeholder="3"></span>
                </li>

            </ul>
          </p>
          <p>
            <input type="submit" class="btn btn-info" value="Compute Histogram(s)">
          </p>
        </form>`+'</div>').appendTo('.tab-content');

    	// make the new tab active
    	$('#tabs a:last').tab('show');
        assignButtons();
        ajaxCall();
  });
});

function assignButtons(){
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    var cells = document.querySelectorAll('input[type="number"]');

    for (var i = 0; i < checkboxes.length; i++) {
        var closureMaker = function(i) {
            return function(event){
                if(checkboxes[i].checked){
                    cells[i].style.display = "inline";
                    cells[i].value = "5";
                    cells[i].required = "true";
                } else {
                    cells[i].style.display = "none";
                    cells[i].value = "";
                    cells[i].required = "false";
                }
            };
        };
        var closure = closureMaker( i );
        checkboxes[i].addEventListener('click', closure, false);
    }
}
assignButtons();

ajaxCall = function(){
    var forms = document.getElementsByTagName("FORM");
    for (var i=0; i<forms.length; i++){
        var formId = forms[i].id;
        var tabid = forms[i].parentElement.id;
        $('#'+formId).ajaxForm({
            success : function (response) {
                document.getElementById(tabid).innerHTML = '<iframe width="900" height="800" frameborder="0" scrolling="no" src="' + response+ '"></iframe>';
            }
        });
    }
};
ajaxCall();