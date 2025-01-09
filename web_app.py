import cherrypy
import os
import re 
import traceback 
import error_msg
import helper
import csv
import pandas as pd
import json
from  cherrypy.lib.static import serve_file

#make global data frame
global data_frame
data_frame = pd.DataFrame()
with open("./tsvFiles/filtered_AllGEO.tsv", "r", encoding="utf-8") as meta_file:
    data_frame = pd.read_csv(meta_file, sep="\t") 

#global database_ids
global database_ids
with open("./tsvFiles/filtered_AllGEO_ids.tsv", "r", encoding="utf-8") as id_file:
    all_geo_ids = pd.read_csv(id_file, sep="\t") 
with open("./tsvFiles/gte_ids.tsv", "r", encoding="utf-8") as id_file:
    gte_ids = pd.read_csv(id_file, sep="\t") 
gte_ids_set = set(gte_ids['GSE'])
all_geo_ids_set = set(all_geo_ids['GSE'])
database_ids = gte_ids_set & all_geo_ids_set

class WebApp:

    @cherrypy.expose
    def index(self):
        global data_frame
        # renders the starting page
        try:
            return self.head() + self.search_home() + self.footer()
        except:
            with open("error.txt", "w", encoding="utf-8") as error_file:
                traceback.print_exc(file=error_file)
            return error_msg.render_error()
    
    @cherrypy.expose
    def about(self):
        return self.head() + self.read_text_file("./htmlFiles/about.html") + self.footer()
    
    @cherrypy.expose
    def head(self):
        return self.read_text_file("./htmlFiles/head.html")
    
    @cherrypy.expose
    def search_home(self):
        return self.read_text_file("./htmlFiles/search_home.html")
    
    @cherrypy.expose
    def footer(self):
        return self.read_text_file("./htmlFiles/footer.html")
    
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

    #generates results once user input is received. called from the query function
    def bottom_half_html(self, ids, metadata_dct):
        return f"""
                    <div class="columns is-centered" id="results">
                        {self.validate_input(ids, metadata_dct)}      
                    </div>
                    
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
            return '<caption class="py-4 mt-3 subtitle is-3 has-text-centered is-family-sans-serif">ERROR:</caption>' + \
                error_msg.num_samples_error_msg() 
        
        if metadata_dct["Experiment_Type"] == []:
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

        '''#renders error message on screen if user has input an invalid ID or an invalid year
        message = ''
        if bad_format_ids or not_found_ids:  
            message += 'ERROR: ' + error_msg.invalid_input_msg(bad_format_ids, not_found_ids, valid_ids)
        if bad_format_years or not_found_years:
            message +=  'ERROR: ' + error_msg.invalid_year_msg(bad_format_years, not_found_years, valid_years)


        #if all entered ID's and years were valid, calls generate_rows to get results
        if valid_ids:
            message += WebApp.generate_rows(valid_ids=valid_ids, metadata_dct=metadata_dct)

        return message'''

        # Renders error message on screen if user has input an invalid ID or an invalid year
        message = ''
        if bad_format_ids or not_found_ids:
            message += f'<div class="error-message">ERROR: {error_msg.invalid_input_msg(bad_format_ids, not_found_ids, valid_ids)}</div>'

        if bad_format_years or not_found_years:
            message += f'<div class="error-message">ERROR: {error_msg.invalid_year_msg(bad_format_years, not_found_years, valid_years)}</div>'

        # If all entered IDs and years were valid, call generate_rows to get results
        if valid_ids:
            message += f'<div></div><div class="search-results">{WebApp.generate_rows(valid_ids=valid_ids, metadata_dct=metadata_dct)}</div>'

        # Ensure there is space between error and results
        return message

    #calls generate_query_results and writes results in html code, to display results in a table 
    def generate_rows(valid_ids=[], metadata_dct={}):

        filtered_df = helper.filter_by_metas(metadata_dct)
        filtered_ids = filtered_df["GSE"].to_list()

        #queries the collection to get most similar results based on user's valid ID's
        if valid_ids:
            results_ids = helper.generate_id_query_results(valid_ids)
        
        #creates a list of ID's, where the filtered ID's and query ID's overlap
        match_ids = [value for value in results_ids if value in filtered_ids]

        results_df = filtered_df[filtered_df["GSE"].isin(match_ids)]
        results_df = results_df.reset_index(drop=True)
        
        # start of process to convert the dataframe to a javascript array 
        # table_info = results_df.to_dict(orient='records')
        # json.dumps(table_info)

        table = '''
            <table class="table is-size-medium mx-6 is-centered" id="myTable" border="1">
            <caption>Relevant Studies:</caption>
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
                </thead><tbody>'''
        for id in match_ids:
            line = filtered_df[filtered_df["GSE"] == id]
            table += f'<tr> <td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={id}">{id}</a></td> \
                <td>{line["Summary"].values[0]}</td> \
                <td>{line["Species"].values[0]}</td> <td>{line["Num_Samples"].values[0]}</td> \
                <td>{line["Experiment_Type"].values[0]}</td> \
                <td>{line["Year_Released"].values[0]}</td> \
                <td>{line["SuperSeries_GSE"].values[0]}</td> \
                <td>{line["SubSeries_GSE"].values[0]}</td> </tr>'
        table += '</tbody></table>'
        return table
    
if __name__ == '__main__':
    style_path = os.path.abspath("styles.css")
    icon_path = os.path.abspath("geo_logo.ico")
    pagination_path = os.path.abspath("pagination.js")

    cherrypy.quickstart(WebApp(), "/", {
            '/styles.css':
            {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': style_path
            },
            '/geo_logo.ico':
            {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': icon_path
            },
            '/pagination.js':
            {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': pagination_path
            }
    })

'''
TO-DO, in order
- Create help button with instructions of how to upload a file from GSE
- fix error message formatting
- later: pagination (idea: copy/paste contents from pagination.js straight into the script tag of the webapp)
- error: after trying to upload a file and trying to type an ID in, it doesn't work.

DONE 1/9:
- added in new gte-large file
- fixed so that results for valid ID's are displayed even when there are others with errors
- added about page info (eventually we will link it to bioarchive)
- added error handling for if a user uploads a file with no GSE ID's

questions:
- with new gte-large file, is it supposed to have embeddings for all ID's in GEO now?
- formatting: error message alongside table of data for valid ID's

#context of our project to give to chat when asking questions
im making a web app and im using python, html, and css for the backend with javascript for the frontend. 
im using cherrypy as the framework. right now im trying to use javascript to implement pagination on the results i display, but it isn't working.
'''