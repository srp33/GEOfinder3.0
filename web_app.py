# Final Copy
import cherrypy
import re 
import traceback 
import error_msg
import helper
import csv

class WebApp:

    @cherrypy.expose
    def index(self):
        try:
            return self.top_half_html()
        except:
            with open("error.txt", "w") as error_file:
                traceback.print_exc(file=error_file)
            return error_msg.render_error()

    # a) 1-10, b) 11-50, c) 51-100, d) 101-500, e) 501-1000, f) 1000+
    @cherrypy.expose
    def query(self, ids, a="", b="", c="", d="", e="", f="", rnaSeq="", microarr=""):
        metadata_dct = self.make_metadata_dct([a, b, c, d, e, f], [rnaSeq, microarr])
        try:
            return self.bottom_half_html(ids, metadata_dct)
        except:
            with open("error.txt", "w") as error_file:
                traceback.print_exc(file=error_file)
            return error_msg.render_error()

    #Internal:

    #returns dictionary containing the user's filter selections
    def make_metadata_dct(self, num_samples, experiment_type):
        metadata_dct={}
        if num_samples:
            metadata_dct["Num_Samples"] = [val for val in num_samples if val]
        if experiment_type:
            metadata_dct["Experiment_Type"] = [val for val in experiment_type if val]
        return metadata_dct

    #renders the starting page
    def top_half_html(self):
        with open("top_half_html.txt") as top_html:
            html_str = top_html.read()
            return html_str
    
    #generates results once user input is received. called from the query function
    def bottom_half_html(self, ids, metadata_dct):
        return f"""
        
        <div class="columns is-centered" id="results">
            <div class="columns is-three-quarters">
                <table class="table is-size-medium" id="myTable" border="1">
                    {self.handle_input_ids(ids, metadata_dct)}
                </table>
            </div>
        </div>
        <script> // When results generated, reenable submit button and scroll down to results
            $('#submitButton').prop('disabled', false);
            results.scrollIntoView({{ behavior: "smooth", block: "start" }});
        </script>
        </body>
        </html>
        """

    #checks for invalid ID input, if all input is valid then calls generate_rows 
    def handle_input_ids(self, ids, metadata_dct):
        database_ids = helper.generate_database_ids()
        
        if (ids == ""):
            return ""  
        else:
            id_lst = re.split(r"\n|,",ids.strip())
            bad_format_ids = []
            not_found_ids = []
            valid_ids = []

            for id in id_lst:
                id = id.strip().upper()

                if not re.search(r"GSE\d+",id):
                    bad_format_ids.append(id)
                elif id not in database_ids:
                    not_found_ids.append(id)
                else: 
                    valid_ids.append(id)
            
            #renders error message on screen if user has input an invalid ID
            if bad_format_ids or not_found_ids:    
                return '<caption class="py-4 mt-3 subtitle is-3 has-text-centered is-family-sans-serif">ERROR:</caption>' + \
                    error_msg.invalid_id_msg(bad_format_ids, not_found_ids, valid_ids)
            #if all entered ID's were valid, calls generate_rows to get results
            else:
                return WebApp.generate_rows(valid_ids=valid_ids, metadata_dct=metadata_dct)

    #calls generate_query_results and writes results in html code, to display results in a table 
    def generate_rows(valid_ids=[], metadata_dct={}):

        filtered_df = helper.filter_by_metas(metadata_dct)
        filtered_ids = filtered_df["GSE"].to_list()

        #queries the collection to get most similar results based on user's valid ID's
        if valid_ids:
            results_ids = helper.generate_id_query_results(valid_ids)
        
        #creates a list of ID's, where the filtered ID's and query ID's overlap
        match_ids = [value for value in results_ids if value in filtered_ids]

        rows = '<caption class="py-4 mt-3 subtitle is-3 has-text-centered is-family-sans-serif">Relevant Studies:</caption>' + \
                '<tr> <th>GSE ID</th> <th>Summary</th> <th>Species</th> <th># Samples</th> <th>Experiment Type</th></tr>'

        #prints data to table for each match ID
        for id in match_ids:
            line = filtered_df[filtered_df["GSE"] == id]
            rows += f'<tr> <td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={id}">{id}</a></td> \
                <td>{line["Summary"].values[0]}</td> \
                <td>{line["Species"].values[0]}</td> <td>{line["Num_Samples"].values[0]}</td> \
                <td>{line["Experiment_Type"].values[0]}</td> </tr>'
        return rows

if __name__ == '__main__':
    cherrypy.quickstart(WebApp(), '/')


'''
9/17
- 1. make data frame from filtered tsv file when you start the webapp (before user inputs anything)
- 2. when user queries, make a copy of the dataframe and filter - experiment_type.startswith("array") or .endswith("sequencing"), num_samples is an exact match

TO-DO
- small thing: fix submit button functionality 
- bulma - configure so that table rows alternate colors for readability
- if filtering by year, look for info in "6/4 update" email chain w Dr. Piccolo

questions:
- lines 39-49 of helper, is there a better way to merge?
- where can we store the list of gse ids ? So that it doesn't have to be reloaded each time (helper line 102)
- in helper line 74 we have num_results=50, is that the number we want to stick with?
'''