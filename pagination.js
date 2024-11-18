var array_length = 1000;
var table_size = 10;
var start_index = 1;
var end_index = 0;
var current_index = 1;
var max_index = 0;

function preLoadCalculations(){
    var array = JSON.parse(table_info);
    console.log("Array: " + array)
    array_length = array.length;
    max_index = Math.floor(array_length / table_size);

    if((array_length % table_size) > 0){
        max_index++;
    }
}

function displayIndexButtons(){
    $(".index_buttons button").remove();
    //Append previous and next buttons
    $(".index_buttons").append('<button onclick= "prev();">Previous</button>');
    $(".index_buttons").append('<button onclick= "next();">Next</button>');

    //Disable "Previous" button if on the first page
    if(current_index <= 1) {
        $(".index_buttons button:first").prop('disabled', true);
    } else {
        $(".index_buttons button:first").prop('disabled', false);
    }

    //Disable "Next" button if on the last page
    if(current_index >= max_index) {
        $(".index_buttons button:last").prop('disabled', true);
    } else {
        $(".index_buttons button:last").prop('disabled', false);
    }
}

displayIndexButtons();

function highlightIndexButton(){
    start_index = ((current_index - 1) * table_size) + 1;
    end_index = (start_index + table_size) - 1;
    if (end_index > array_length) {
        end_index = array_lenegth;
    }
    $(".pagination span").text('Showing '+start_index+' to '+end_index+' of '+array_length+' entries');
}

function displayTableRows(){
    $(".table table tbody tr").remove();
    var tab_start = start_index - 1;
    var tab_end = end_index;

    for(var i=tab_start; i<tab_end; i++){
        var curr_ID = array[i];
        var tr = `<tr>
            <td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=${curr_ID}">${curr_ID}</a></td>
            <td>${curr_ID["Summary"].values[0]}</td>
            <td>${curr_ID["Species"].values[0]}</td>
            <td>${curr_ID["Num_Samples"].values[0]}</td>
            <td>${curr_ID["Experiment_Type"].values[0]}</td>
            <td>${curr_ID["Year_Released"].values[0]}</td>
            <td>${curr_ID["SuperSeries_GSE"].values[0]}</td>
            <td>${curr_ID["SubSeries_GSE"].values[0]}</td>
          </tr>`;
    }
}

function next(){
    if(currentIndex < max_index){
        current_index++;
        highlightIndexButton();
        displayTableRows();
    }
}

function prev(){
    if(current_index > 1){
        current_index--;
        highlightIndexButton();
        displayTableRows();
    }
}

$(document).ready(function() {
    // Attach event listeners to the buttons
    $('#prev-btn').click(function() {
        prev();  // Calls the prev() function when the "Previous" button is clicked
        console.log("prev button listener worked");
    });
    
    $('#next-btn').click(function() {
        next();  // Calls the next() function when the "Next" button is clicked
        console.log("next  button listener worked");
    });
});
