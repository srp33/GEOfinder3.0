import cherrypy
from cherrypy.lib.static import serve_file
from datetime import datetime
import numpy as np
import os
import pandas as pd
import re
import traceback

class WebApp:
    @cherrypy.expose
    def index(self):
        try:
            return self.header() + self.search_home() + self.footer()
        except:
            return self.header() + self.format_error_msg(traceback.format_exc()) + self.footer()

    @cherrypy.expose
    def about(self):
        try:
            return self.header() + self.read_text_file("htmlFiles/about.html") + self.footer()
        except:
            return self.header() + self.format_error_msg(traceback.format_exc()) + self.footer()

    # a) 1-10, b) 11-50, c) 51-100, d) 101-500, e) 501-1000, f) 1000+
    @cherrypy.expose
    def query(self, ids, a="", b="", c="", d="", e="", f="", rnaSeq="", microarr="", startYear="", endYear=""):
        try:
            # This should be robust to extract characters, inconsistent capitalization, etc.
            ids = re.findall(r'GSE\d{1,8}', ids, re.IGNORECASE)
            ids = [id.upper() for id in ids]

            metadata_dict = self.make_metadata_dct([a, b, c, d, e, f], [rnaSeq, microarr], [startYear, endYear])

            if len(ids) == 0:
                return self.format_error_msg("No valid accession identifiers were provided.")

            not_found_ids = self.validate_ids(ids)
            if len(not_found_ids) > 0:
                return self.format_error_msg(f'''The following ID(s) you entered are currently not available in GEOfinder: {', '.join(not_found_ids)}. This could be because they are not valid GEO accession number(s) or that we have filtered them for some reason.''')

            if metadata_dict["Num_Samples"] == []:
                return self.format_error_msg("Please check at least one box indicating the number of samples per data series.")
            
            if metadata_dict["Experiment_Type"] == []:
                return self.format_error_msg("Please check at least one box indicating the experiment type(s).")
            
            matching_df = self.filter_by_metas(metadata_dct)
            
            # WebApp.generate_rows(valid_ids=valid_ids, metadata_dct=metadata_dct)

            #             elif (self.validate_checkboxes(metadata_dct)):
            #     return format_error_msg("Error: Please check at least one box for each filter category.")

            return self.format_error_msg("test")
            # return self.bottom_half_html(ids, metadata_dict)
        except:
            return self.format_error_msg(traceback.format_exc())

    ####################################################
    # Private functions
    ####################################################

    def read_text_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as the_file:
            return the_file.read()
        
    def header(self):
        return self.read_text_file("htmlFiles/header.html")
    
    def search_home(self):
        thisYear = datetime.now().year

        startYearHtml = "<option selected>2001</option>\n"
        for year in range(2002, thisYear + 1):
            startYearHtml += f"<option>{year}</option>\n"

        endYearHtml = ""
        for year in range(2001, thisYear):
            endYearHtml += f"<option>{year}</option>\n"

        endYearHtml = f"<option selected>{thisYear}</option>"

        return self.read_text_file("htmlFiles/search_home.html").replace("{{ startYears }}", startYearHtml).replace("{{ endYears }}", endYearHtml)

    def footer(self):
        return self.read_text_file("htmlFiles/footer.html")

    # Return a dictionary containing the user's filter selections.
    def make_metadata_dct(self, num_samples, experiment_type, years):
        metadata_dct={}

        if num_samples:
            metadata_dct["Num_Samples"] = [val for val in num_samples if val]

        if experiment_type:
            metadata_dct["Experiment_Type"] = [val for val in experiment_type if val]

        if years:
            metadata_dct["Years"] = years

        return metadata_dct
    
    def validate_ids(self, ids):
        not_found_ids = []

        for id in ids:
            if id not in data_frame.index:
                not_found_ids.append(id)

        return not_found_ids

    def format_error_msg(self, msg):
        return f"<div class='content has-text-left is-size-5'><pre class='has-text-danger'>{msg}</pre></div>"
    
    # Returns a dataframe, filtered based on the user's selections.
    def filter_by_metas(self, metadata_dct):
        # global data_frame
        df_copy = data_frame.copy(deep=True)

        # Filter the dataframe copy based on experiment type.
        if metadata_dct["Experiment_Type"]:
            if len(metadata_dct["Experiment_Type"]) == 1:
                if metadata_dct["Experiment_Type"][0]== "Microarray":
                    df_copy = df_copy[df_copy["Experiment_Type"].str.startswith("Expression profiling by array")]
                elif metadata_dct["Experiment_Type"][0] == "RNA sequencing":
                    df_copy = df_copy[df_copy["Experiment_Type"].str.endswith("Expression profiling by high throughput sequencing")]

        # Filter based on number of samples.
        if metadata_dct["Num_Samples"]:
            #add selected sample numbers to dataframe
            #df_copy = df_copy[df_copy["Samples_Range"] in metadata_dct["Num_Samples"]]
            df_copy = df_copy[df_copy["Samples_Range"].isin(metadata_dct["Num_Samples"])]

        # Filter based on by year.
        df_copy["Year_Released"] = pd.to_numeric(df_copy["Year_Released"], errors='coerce')
        df_copy = df_copy[(df_copy["Year_Released"] >= int(metadata_dct["Years"][0])) & (df_copy["Year_Released"] <= int(metadata_dct["Years"][1]))]
        return df_copy

    # Generates results once user input is received.
    def bottom_half_html(self, ids, metadata_dct):
        return f"""
                    <div id="results">
                        {self.validate_input(ids, metadata_dct)}
                    </div>

                    <script>
                        $('#submitButton').prop('disabled', false);
                        document.getElementById('results').scrollIntoView({{ behavior: "smooth", block: "start" }});
                    </script>
                </body>
            </html>
            """

# Returns a dictionary of the closest results to the user IDs input.
def generate_id_query_results(input_ids):
    chroma_client = chromadb.PersistentClient(path="data/Embeddings")
    my_collection = chroma_client.get_collection(name="geo_collection")

    input_embeddings = []

    for id in input_ids:
        data_dict = my_collection.get(ids=id, include=["embeddings"])
        input_embeddings.append(data_dict["embeddings"][0])

    input_embeddings = np.array(input_embeddings)
    avg_embedding = np.mean(input_embeddings, axis=0).tolist()

    similarityResults = my_collection.query(query_embeddings=avg_embedding, n_results=50)

    return similarityResults["ids"][0]

# Calls generate_query_results and writes results in html code, to display results in a table.
def generate_rows(valid_ids=[], metadata_dct={}):
    filtered_df = helper.filter_by_metas(metadata_dct)
    filtered_ids = filtered_df["GSE"].to_list()

    # Queries the collection to get most similar results based on user's valid ID's.
    if valid_ids:
        results_ids = helper.generate_id_query_results(valid_ids)

    # Creates a list of ID's, where the filtered ID's and query ID's overlap.
    match_ids = [value for value in results_ids if value in filtered_ids]

    results_df = filtered_df[filtered_df["GSE"].isin(match_ids)]
    results_df = results_df.reset_index(drop=True)

    table = f'''
        <table class="table is-centered" id="myTable" border="1">
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

    # The range of this for loop makes it so that the ID that a user is querying on is not included in the results table.
    for i in range((len(valid_ids)), len(match_ids)):
        id=match_ids[i]
        line = filtered_df[filtered_df["GSE"] == id]

        table += f'''<tr> <td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={id}" target="_blank">{id}</a></td> \
            <td>{line["Summary"].values[0]}</td> \
            <td>{line["Species"].values[0]}</td> <td>{line["Num_Samples"].values[0]}</td> \
            <td>{line["Experiment_Type"].values[0]}</td> \
            <td>{line["Year_Released"].values[0]}</td> \
            <td>{line["SuperSeries_GSE"].values[0]}</td> \
            <td>{line["SubSeries_GSE"].values[0]}</td> </tr>'''
    
    table += f'''</tbody></table>'''
    
    return table

if __name__ == '__main__':
    style_path = os.path.abspath("styles.css")
    icon_path = os.path.abspath("geo_logo.ico")
    # pagination_path = os.path.abspath("pagination.js")

    global data_frame
    data_frame = pd.read_csv("data/FilteredGEO.tsv.gz", sep="\t", index_col=0)

    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
    })

    cherrypy.quickstart(WebApp(), "/geofinder", {
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
    })