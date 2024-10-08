# Final Copy
import cherrypy
import re 
import traceback 
import error_msg
import helper
import csv
import pandas as pd

#make global data frame
global data_frame
data_frame = pd.DataFrame()
with open("filtered_AllGEO.tsv", "r") as meta_file:
    data_frame = pd.read_csv(meta_file, sep="\t") 

#global database_ids
global database_ids
database_ids = set(data_frame["GSE"])

class WebApp:

    @cherrypy.expose
    def index(self):
        global data_frame
        
        try:
            return self.top_half_html()
        except:
            with open("error.txt", "w") as error_file:
                traceback.print_exc(file=error_file)
            return error_msg.render_error()

    # a) 1-10, b) 11-50, c) 51-100, d) 101-500, e) 501-1000, f) 1000+
    @cherrypy.expose
    def query(self, ids, a="", b="", c="", d="", e="", f="", rnaSeq="", microarr="", startYear="", endYear=""):
        metadata_dct = self.make_metadata_dct([a, b, c, d, e, f], [rnaSeq, microarr], [startYear, endYear])
        print("metadata_dct", metadata_dct)
        try:
            return self.bottom_half_html(ids, metadata_dct)
        except:
            with open("error.txt", "w") as error_file:
                traceback.print_exc(file=error_file)
            return error_msg.render_error()

    #Internal:

    #returns dictionary containing the user's filter selections
    def make_metadata_dct(self, num_samples, experiment_type, years):
        metadata_dct={}
        if num_samples:
            metadata_dct["Num_Samples"] = [val for val in num_samples if val]
        if experiment_type:
            metadata_dct["Experiment_Type"] = [val for val in experiment_type if val]
        if years:
            metadata_dct["Years"] = [val for val in years if val]
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
                    {self.validate_input(ids, metadata_dct)}
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
    def validate_input(self, ids, metadata_dct):
        global database_ids
        #validates ID input
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

        #validates year input          
        bad_format_years = []
        not_found_years = []
        valid_years = []
        startYear = metadata_dct["Years"][0]
        endYear = metadata_dct["Years"][1]

        if not re.search(r"^\d{4}$", startYear):
            bad_format_years.append(startYear)
        if int(startYear)<2001 or int(startYear)>2024:
            not_found_years.append(startYear)

        if not re.search(r"^\d{4}$", endYear):
            bad_format_years.append(endYear)
        if int(endYear)<2001 or int(endYear)>2024:
            not_found_years.append(endYear)

        if(bad_format_years==[] and not_found_years==[]):  
            print("both valid formats and years")     
            if(int(endYear) >= int(startYear)):
                valid_years.append(startYear)
                valid_years.append(endYear)
            else:
                bad_format_years.append(startYear)
                bad_format_years.append(endYear)

        #renders error message on screen if user has input an invalid ID or an invalid year
        if bad_format_ids or not_found_ids or bad_format_years or not_found_years: 
            print("error detected")   
            return '<caption class="py-4 mt-3 subtitle is-3 has-text-centered is-family-sans-serif">ERROR:</caption>' + \
                error_msg.invalid_input_msg(bad_format_ids, not_found_ids, valid_ids, bad_format_years, not_found_years, valid_years)
        #if all entered ID's and years were valid, calls generate_rows to get results
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
                '<tr> <th>GSE ID</th> <th>Summary</th> <th>Species</th> <th># Samples</th> <th>Experiment Type</th> <th>Year Released</th><th>Super Series</th> <th>Sub Series</th></tr>'

        #prints data to table for each match ID
        for id in match_ids:
            line = filtered_df[filtered_df["GSE"] == id]
            rows += f'<tr> <td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={id}">{id}</a></td> \
                <td>{line["Summary"].values[0]}</td> \
                <td>{line["Species"].values[0]}</td> <td>{line["Num_Samples"].values[0]}</td> \
                <td>{line["Experiment_Type"].values[0]}</td> \
                <td>{line["Year_Released"].values[0]}</td> \
                <td>{line["SuperSeries_GSE"].values[0]}</td> \
                <td>{line["SubSeries_GSE"].values[0]}</td> <tr>'
        return rows

if __name__ == '__main__':
    cherrypy.quickstart(WebApp(), '/')


'''
filter/query process
- 1. make data frame from filtered tsv file when you start the webapp (before user inputs anything)
- 2. when user queries, make a copy of the dataframe and filter - experiment_type.startswith("array") or .endswith("sequencing"), num_samples is an exact match

TO-DO
- if filtering by year, look for info in "6/4 update" email chain w Dr. Piccolo

questions:
- lines 39-49 of helper, is there a better way to merge?
- where can we store the list of gse ids ? So that it doesn't have to be reloaded each time (helper line 102)
- in helper line 74 we have num_results=50, is that the number we want to stick with?

9/30
- getting the webapp working on amanda's computer
- look at other filtering options

10/1
- generate database ids from global dataframe using tolist function of pandas --> convert that list to a set
- later, once we have everything else done, explore how to have num_results>50 with multiple pages (consistent with the paper to use 1000)
- option to upload a file of search results from GEO (after checking boxes on GEO/downloading result file) - upload that file and we parse it to get GSE ID's and search
- webapp name - GEOfinder, make logo
- add footer - BYU disclaimers, etc (copy basic one from codebuddy)

10/3
DONE:
- year inputs
- modified tsv file, added samples_range, year, super and sub series columns
- changed filtering method for num samples
- filtered by year
- display super/sub series on table as output
- display year on table (make sure filtering was done right)

TO-DO, in order
- create database ids as a global set 
- fix table formatting (extend to end of screen on the right)
- flip logic for super/sub series

#breaks for this ID: GSE233796, GSE233785
'''