# Final Copy
import cherrypy
import os
import re 
import traceback 
import error_msg
import helper
import csv
import pandas as pd
import json

#make global data frame
global data_frame
data_frame = pd.DataFrame()
with open("filtered_AllGEO.tsv", "r", encoding="utf-8") as meta_file:
    data_frame = pd.read_csv(meta_file, sep="\t") 

#global database_ids
global database_ids
with open("filtered_AllGEO_ids.tsv", "r", encoding="utf-8") as id_file:
    all_geo_ids = pd.read_csv(id_file, sep="\t") 
with open("gte_ids.tsv", "r", encoding="utf-8") as id_file:
    gte_ids = pd.read_csv(id_file, sep="\t") 
gte_ids_set = set(gte_ids['GSE'])
all_geo_ids_set = set(all_geo_ids['GSE'])
database_ids = gte_ids_set & all_geo_ids_set

class WebApp:

    @cherrypy.expose
    def index(self):
        global data_frame
        print("in index")
        try:
            print("in try block")
            return self.top_half_html()
        except:
            with open("error.txt", "w", encoding="utf-8") as error_file:
                traceback.print_exc(file=error_file)
            return error_msg.render_error()
    
    @cherrypy.expose
    def about(self):
        return "hello"
    
    @cherrypy.expose
    def pagination_js(self):
        return self.read_text_file("...../pagination.js")

    # a) 1-10, b) 11-50, c) 51-100, d) 101-500, e) 501-1000, f) 1000+
    @cherrypy.expose
    def query(self, ids, a="", b="", c="", d="", e="", f="", rnaSeq="", microarr="", startYear="", endYear=""):
        metadata_dct = self.make_metadata_dct([a, b, c, d, e, f], [rnaSeq, microarr], [startYear, endYear])
        try:
            return self.bottom_half_html(ids, metadata_dct)
        except:
            with open("error.txt", "w", encoding="utf-8") as error_file:
                traceback.print_exc(file=error_file)
            return error_msg.render_error()

    #Internal:

    def read_text_file(self, file_path):
        with open(file_path) as the_file:
            return the_file.read()

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
        with open("top_half.html") as top_html:
            html_str = top_html.read()
            return html_str
    
    #generates results once user input is received. called from the query function
    def bottom_half_html(self, ids, metadata_dct):
        return f"""
                    <h2 class="py-4 mt-3 has-text-centered">Relevant Studies:</h2>
                    <div class="columns is-centered" id="results">
                        <table class="table is-size-medium mx-6" id="myTable" border="1">
                            <thead>
                                <tr>
                                    <th>GSE ID</th>
                                    <th>Summary</th>
                                    <th>Species</th>
                                    <th># Samples</th>
                                    <th>Experiment Type</th>
                                    <th>Year Released</th>
                                    <th>Super Series</th>
                                    <th>Sub Series</th>
                                </tr>
                            </thead>
                            <tbody>
                                {self.validate_input(ids, metadata_dct)}
                            </tbody>
                        </table>        
                    </div>
                    <nav class="pagination" role="navigation" aria-label="pagination">   
                        <span>Showing 1 to 50 of 1000 results</span> 
                        <div class = "index_buttons">
                            <button class="pagination-previous" id="prev-btn">Previous</button>
                            <button class="pagination-next" id="next-btn">Next</button>
                        </div>
                    </nav>
                    <script src="/pagination_js"></script> 
                    <script>
                        $('#submitButton').prop('disabled', false);
                        document.getElementById('results').scrollIntoView({{ behavior: "smooth", block: "start" }});
                    </script>
                </body>
            </html>
            """

    #checks for invalid ID input, if all input is valid then calls generate_rows 
    def validate_input(self, ids, metadata_dct):
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

        #make sure some boxes are checked
        if metadata_dct["Num_Samples"] == []:
            print("error detected")   
            return '<caption class="py-4 mt-3 subtitle is-3 has-text-centered is-family-sans-serif">ERROR:</caption>' + \
                error_msg.num_samples_error_msg() 
        
        if metadata_dct["Experiment_Type"] == []:
            print("error detected")
            return '<caption class="py-4 mt-3 subtitle is-3 has-text-centered is-family-sans-serif">ERROR:</caption>' + \
                error_msg.experiment_error_msg() 

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
        if bad_format_ids or not_found_ids: 
            print("error detected")   
            return '<caption class="py-4 mt-3 subtitle is-3 has-text-centered is-family-sans-serif">ERROR:</caption>' + \
                error_msg.invalid_input_msg(bad_format_ids, not_found_ids, valid_ids) 
        if bad_format_years or not_found_years:
            print("error detected")
            return '<caption class="py-4 mt-3 subtitle is-3 has-text-centered is-family-sans-serif">ERROR:</caption>' + \
                error_msg.invalid_year_msg(bad_format_years, not_found_years, valid_years)

        #if all entered ID's and years were valid, calls generate_rows to get results
        else:
            return WebApp.generate_rows(valid_ids=valid_ids, metadata_dct=metadata_dct)

    #calls generate_query_results and writes results in html code, to display results in a table 
    def generate_rows(valid_ids=[], metadata_dct={}):

        filtered_df = helper.filter_by_metas(metadata_dct)
        #print("filtered df length: ", len(filtered_df))
        #print("filtered df: ", filtered_df.head())
        filtered_ids = filtered_df["GSE"].to_list()

        #queries the collection to get most similar results based on user's valid ID's
        if valid_ids:
            results_ids = helper.generate_id_query_results(valid_ids)
        
        #creates a list of ID's, where the filtered ID's and query ID's overlap
        match_ids = [value for value in results_ids if value in filtered_ids]
        #print("match ids length:", len(match_ids))

        results_df = filtered_df[filtered_df["GSE"].isin(match_ids)]
        results_df = results_df.reset_index(drop=True)
        #print("results df length: ", len(results_df))
        #print("results df: ", results_df.head())
        table_info = results_df.to_dict(orient='records')
        #print(table_info)
        json.dumps(table_info)

        # for id in match_ids:
        #     line = filtered_df[filtered_df["GSE"] == id]
        #     rows += f'<tr> <td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={id}">{id}</a></td> \
        #         <td>{line["Summary"].values[0]}</td> \
        #         <td>{line["Species"].values[0]}</td> <td>{line["Num_Samples"].values[0]}</td> \
        #         <td>{line["Experiment_Type"].values[0]}</td> \
        #         <td>{line["Year_Released"].values[0]}</td> \
        #         <td>{line["SuperSeries_GSE"].values[0]}</td> \
        #         <td>{line["SubSeries_GSE"].values[0]}</td> </tr>'

        #prints data to table for each match ID
        rows = ''
        for id in match_ids:
            line = filtered_df[filtered_df["GSE"] == id]
            rows += f'<tr> <td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={id}">{id}</a></td> \
                <td>{line["Summary"].values[0]}</td> \
                <td>{line["Species"].values[0]}</td> <td>{line["Num_Samples"].values[0]}</td> \
                <td>{line["Experiment_Type"].values[0]}</td> \
                <td>{line["Year_Released"].values[0]}</td> \
                <td>{line["SuperSeries_GSE"].values[0]}</td> \
                <td>{line["SubSeries_GSE"].values[0]}</td> </tr>'
        return rows

# Create the app and mount it, including static serving
cherrypy.tree.mount(WebApp(), '/', {
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': "/Users/amand/OneDrive/Desktop/Piccolo Lab/GEOfinder3.0/static"
    }
})

if __name__ == '__main__':
    cherrypy.quickstart(WebApp())


'''
10/14-10/20
TO-DO, in order
- webapp name - GEOfinder, make logo
- use bulma to have num_results>50 with multiple pages (consistent with the paper to use 1000)
- option to upload a file of search results from GEO (after checking boxes on GEO/downloading result file) - upload that file and we parse it to get GSE ID's and search

questions:
- footer all the way at the bottom
- where we left off monday: need to check line 1 of pagination.js

11/7
- pagination.js gives a 404 error, file not found. We can add it to a /static folder and configure cherrypy to serve static files
- We will also have to change how we refer to it in the html
- There are also event listeners and console logs to help with debugging
- clicked go live and the  aout page came back but the results don't load

'''
'''
#checks that we're merging the allGEO and gte-large ids correctly
missing_ids = gte_ids_set - all_geo_ids_set

overlapping_ids_list = list(overlap_ids)
print("Number of overlapping GSE values:", len(overlapping_ids_list))
missing_ids_list = list(missing_ids)
print("Missing GSE values:", missing_ids_list)
print("Number of missing GSE values:", len(missing_ids_list))
'''