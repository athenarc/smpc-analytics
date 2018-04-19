function addTab() {
  var nextTab = $('#tabs li').length;

  // remove the button from the end
  var add_btn = document.getElementById('btnAdd');
  add_btn.parentElement.remove();

  // create the tab and add it to the end
  $('<li class="nav-item"><a class="nav-link" href="#tab'+nextTab+'" id="tab'+nextTab+'-tab" data-toggle="tab">Histogram '+nextTab+'</a></li>').appendTo('#tabs');

  // create the tab content
  $('<div class="tab-pane fade" id="tab'+nextTab+'">' +
      `<div style="display: none;" id="loading-wrapper_hist_`+nextTab+`">
        <div id="loading-text">LOADING</div>
        <div id="loading-content"></div>
      </div>` +
      `<form action="/histogram" method="post" id="hist_`+nextTab+`">
        <p>
          <ul class="list-group">
              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="Patient Age"> Patient Age &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="Heart rate"> Heart rate &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="Height (cm)"> Height (cm) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="Weight (kg)"> Weight (kg) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="LVEDV (ml)"> LVEDV (ml) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="LVESV (ml)"> LVESV (ml) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="LVSV (ml)"> LVSV (ml) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="LVEF (%)"> LVEF (%) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="LV Mass (g)"> LV Mass (g) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="RVEDV (ml)"> RVEDV (ml) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="RVESV (ml)"> RVESV (ml) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="RVSV (ml)"> RVSV (ml) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="RVEF (%)"> RVEF (%) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="RV Mass (g)"> RV Mass (g) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="BMI (kg/msq)"> BMI (kg/msq) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="BSA"> BSA &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="BSA (msq)"> BSA (msq) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="CO (L/min)"> CO (L/min) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="Central PP(mmHg)"> Central PP(mmHg) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="DBP (mmHg)"> DBP (mmHg) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="LVEF (ratio)"> LVEF (ratio) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="MAP"> MAP &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="PAP (mmHg)"> PAP (mmHg) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="PP (mmHg)"> PP (mmHg) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="RVEF (ratio)"> RVEF (ratio) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="SBP (mmHg)"> SBP (mmHg) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <li class="list-group-item">
                <input type="checkbox" name="attributes" value="SVR (mmHg/L/min)"> SVR (mmHg/L/min) &ensp;
                <span style="float:right;"><input type="number" name="cells" min="1" max="15" style="display:none;" placeholder="3"></span>
              </li>

              <div id="filter_container_` + nextTab + `"/>
          </ul>
        </p>
        <p>
          <input type="button" id="filter_button_` + nextTab + `" onclick="addFilterToFormWithId(this.id)" class="btn btn-default" value="Add Filter">
        </p>
        <p>
          <ul class="list-group">
              <li class="list-group-item">
                <input type="checkbox" name="datasets" value="data_provider_0" checked="true"> Dataset 1 &ensp;
              </li>
              <li class="list-group-item">
                <input type="checkbox" name="datasets" value="data_provider_1" checked="true"> Dataset 2 &ensp;
              </li>
              <li class="list-group-item">
                <input type="checkbox" name="datasets" value="data_provider_2" checked="true"> Dataset 3 &ensp;
              </li>
          </ul>
        </p>
        <p>
          <input type="submit" id="button_hist_` + nextTab + `" onclick="sendFormWithId(this.id)" class="btn btn-primary" value="Compute Histogram">
        </p>
        </form>`+
    '</div>').appendTo('.tab-content');

  // make the new tab active
  $('#tabs a:last').tab('show');
  assignButtons();

  // add the button to the end
  $('<li class="nav-item"><a href="#" id="btnAdd"><input type="submit" onclick="addTab()" class="btn btn-info btn-sm" value="+" id="tabButton"></input></a></li>').appendTo('#tabs');

  $('.selectpicker').selectpicker();
}

function assignButtons(){
    var checkboxes = document.querySelectorAll('input[name="attributes"]');
    var cells = document.querySelectorAll('input[name="cells"]');
    for (var i = 0; i < checkboxes.length; i++) {
        var closureMaker = function(i) {
            return function(event){
                if(checkboxes[i].checked){
                    cells[i].style.display = "inline";
                    cells[i].value = "5";
                    cells[i].required = "true";
                    cells[i].disabled = false;
                } else {
                    cells[i].style.display = "none";
                    cells[i].value = "";
                    cells[i].required = "false";
                    cells[i].disabled = "disabled";
                }
            };
        };
        var closure = closureMaker( i );
        checkboxes[i].addEventListener('click', closure, false);
    }
}
assignButtons();

function addFilterToFormWithId(formId) {
    var id = formId.substring(14);
    var container = document.getElementById('filter_container_'+id);
    var children = container.childElementCount;
    if (children == 0) {
        var br = document.createElement('br');
        container.appendChild(br);
    }
    var outer_div = document.createElement('div');
    var select_attributes = document.createElement('select');
    select_attributes.name = "filter_" + "attributes";
    select_attributes.form = "hist_" + id;
    select_attributes.className = "selectpicker";
    var attributes = ["Patient Age", "Heart rate", "Height (cm)", "Weight (kg)", "LVEDV (ml)", "LVESV (ml)", "LVSV (ml)", "LVEF (%)", "LV Mass (g)", "RVEDV (ml)", "RVESV (ml)", "RVSV (ml)", "RVEF (%)", "RV Mass (g)", "BMI (kg/msq)", "BSA", "BSA (msq)", "CO (L/min)", "Central PP(mmHg)", "DBP (mmHg)", "LVEF (ratio)", "MAP", "PAP (mmHg)", "PP (mmHg)", "RVEF (ratio)", "SBP (mmHg)", "SVR (mmHg/L/min)"];
    var option = document.createElement('option');
    option.text = "Attribute";
    option.selected = true;
    option.disabled = true;
    select_attributes.appendChild(option);
    for (var i = 0; i < attributes.length; i++){
        option = document.createElement('option');
        option.value = attributes[i];
        option.text = attributes[i];
        select_attributes.appendChild(option);
    }
    outer_div.appendChild(select_attributes);
    space_span = document.createElement('span');
    space_span.innerHTML = " ";
    outer_div.appendChild(space_span);

    var select_op = document.createElement('select');
    select_op.name = "filter_" + "operators";
    select_op.form = "hist_" + id;
    select_op.className = "selectpicker";
    var operators = [">", "<", "="];
    option = document.createElement('option');
    option.text = "Operator";
    option.selected = true;
    option.disabled = true;
    select_op.appendChild(option);
    for (i = 0; i < operators.length; i++){
        option = document.createElement('option');
        option.value = operators[i];
        option.text = operators[i];
        select_op.appendChild(option);
    }
    outer_div.appendChild(select_op);
    space_span = document.createElement('span');
    space_span.innerHTML = " ";
    outer_div.appendChild(space_span);

    var input_div = document.createElement('div');
    input_div.className = "btn-group";
    var input = document.createElement('input');
    input.name = "filter_" + "values";
    input.type = "text";
    input.required = true;
    input.className = "form-control";
    input_div.appendChild(input);
    outer_div.appendChild(input_div);
    space_span = document.createElement('span');
    space_span.innerHTML = " ";
    outer_div.appendChild(space_span);

    if (children == 0) {
        var bool_operators = ["AND", "OR", "XOR"];
        select_op = document.createElement('select');
        select_op.text = "Boolean Operator";
        select_op.name = "boolean_opreator";
        select_op.className = "selectpicker";
        for (i = 0; i < bool_operators.length; i++){
            option = document.createElement('option');
            option.value = bool_operators[i];
            option.text = bool_operators[i];
            select_op.appendChild(option);
        }
        outer_div.appendChild(select_op);
    }
    container.appendChild(outer_div);
    $('.selectpicker').selectpicker();
}

function sendFormWithId(id) {
  var formId = id.substring(7); // get the hist id from the button id
  var tabId = "tab" + formId.substring(5); // get the tab id
  $('#'+formId).ajaxForm({
      beforeSend : function() {
        document.getElementById(formId).style.display = "none"; // hide the attribute list
        document.getElementById('loading-wrapper_'+formId).style.display = "block"; // show the loading sign
      },
      success : function (response) {
        document.getElementById('loading-wrapper_'+formId).style.display = "none"; // hide the loading sign
        document.getElementById(tabId).innerHTML = '<iframe width="900" height="800" frameborder="0" scrolling="no" src="' + response + '"></iframe>';
      }
  });
}

