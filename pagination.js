var array_length = 1000;
var table_size = 10;
var start_index = 1;
var end_index = 0;
var current_index = 1;
var max_index = 0;

function preLoadCalculations(){
    array = json.parse({table_info});
    console.log(array)
    array_length = array.length;
    max_index = parseInt(array_length / table_size);

    if((array_length % table_size) > 0){
        max_index++;
    }
}

function displayIndexButtons(){
    $(".index_buttons button").remove();
    $(".index_buttons").append('<button onclick= "prev();">Previous</button>');
    $(".index_buttons").append('<button onclick= "prev();">Next</button>');
}

displayIndexButtons();

function highlightIndexButton(){
    start_index = ((current_index - 1) - table_size) + 1;
    end_index = (start_index + table_size) - 1;
    if (end_index > array_length){
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
        var tr = <tr> <td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={id}">{id}</a></td> \
                <td>{line["Summary"].values[0]}</td> \
                <td>{line["Species"].values[0]}</td> <td>{line["Num_Samples"].values[0]}</td> \
                <td>{line["Experiment_Type"].values[0]}</td> \
                <td>{line["Year_Released"].values[0]}</td> \
                <td>{line["SuperSeries_GSE"].values[0]}</td> \
                <td>{line["SubSeries_GSE"].values[0]}</td> </tr>;
        $(".table table tbody").append(tr);
    }
}

function next(){
    if(currentIndex < max_index){
        current_index++;
        highlightIndexButton();
    }
}

function prev(){
    if(current_index > 1){
        current_index--;
        highlightIndexButton();
    }
}
