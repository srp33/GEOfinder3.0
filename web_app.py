import cherrypy
from cherrypy.lib.static import serve_file
import chromadb
from datetime import datetime
import gzip
import json
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

    @cherrypy.expose
    def query(self, searchSeries, checkboxDict, startYear, endYear):
        try:
            # This should be robust to extract characters, inconsistent capitalization, etc.
            searchSeries = re.findall(r'GSE\d{1,8}', searchSeries, re.IGNORECASE)
            searchSeries = [id.upper() for id in searchSeries]

            if len(searchSeries) == 0:
                return self.format_error_msg("No valid accession identifiers were provided.")
            
            # # global full_data_frame
            # fullDataFrame = pd.read_csv("data/FilteredGEO.tsv.gz", sep="\t", index_col=0)

            # not_found_ids = self.validate_ids(searchSeries, fullDataFrame)
            # if len(not_found_ids) > 0:
            #     return self.format_error_msg(f'''The following ID(s) you entered are currently not available in GEOfinder: {', '.join(not_found_ids)}. This could be because they are not valid GEO accession number(s) or that we have filtered them for some reason.''')
            
            # checkboxDict = json.loads(checkboxDict)

            # metadataDict, errorMsg = self.make_metadata_dict(checkboxDict, startYear, endYear)

            # if errorMsg != "":
            #     return self.format_error_msg(errorMsg)

            # metaSeries = self.filter_by_metas(metadataDict, fullDataFrame)

            print("aaaaaaaaaaaaaaaaaaaaa")

            metaSeries = []
            embeddingSeries = self.search_embeddings(metaSeries, searchSeries)
            
            # WebApp.generate_rows(valid_ids=valid_ids, metadata_dct=metadata_dct)

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

        experimentTypesHtml = ""
        with gzip.open("data/ExperimentTypes.tsv.gz") as expTypesFile:
            for line in expTypesFile:
                expType = line.decode().rstrip("\n")
                experimentTypesHtml += f"<div class='field'><label class='checkbox'><input type='checkbox' name='{expType}' value='experimentType' checked /> {expType}</label></div>"

        speciesHtml = ""
        with gzip.open("data/Species.tsv.gz") as speciesFile:
            for line in speciesFile:
                species = line.decode().rstrip("\n")
                speciesHtml += f"<div class='field'><label class='checkbox'><input type='checkbox' name='{species}' value='species' checked /> {species}</label></div>"

        return self.read_text_file("htmlFiles/search_home.html").replace("{{ startYears }}", startYearHtml).replace("{{ endYears }}", endYearHtml).replace("{{ experimentTypes }}", experimentTypesHtml).replace("{{ species }}", speciesHtml)

    def footer(self):
        return self.read_text_file("htmlFiles/footer.html")

    def format_error_msg(self, msg):
        return f"<div class='content has-text-left is-size-5'><pre class='has-text-danger'>{msg}</pre></div>"

    def validate_ids(self, ids, fullDataFrame):
        not_found_ids = []

        for id in ids:
            if id not in fullDataFrame.index:
                not_found_ids.append(id)

        return not_found_ids

    # Return a dictionary containing the user's filter selections.
    def make_metadata_dict(self, checkboxDict, startYear, endYear):
        metadataDict={
            "Num_Samples_Range": [],
            "Experiment_Types": [],
            "Species": [],
            "Start_Year": int(startYear),
            "End_Year": int(endYear)
        }

        for checkboxValue, checkboxCategory in checkboxDict.items():
            if checkboxCategory == "numSamplesRange":
                metadataDict["Num_Samples_Range"].append(checkboxValue)
            elif checkboxCategory == "experimentType":
                metadataDict["Experiment_Types"].append(checkboxValue)
            elif checkboxCategory == "species":
                metadataDict["Species"].append(checkboxValue)

        if metadataDict["Num_Samples_Range"] == []:
            return metadataDict, "Please check at least one box indicating the number of samples per data series."

        if metadataDict["Experiment_Types"] == []:
            metadataDict, "Please check at least one box indicating the experiment type(s)."

        if metadataDict["Species"] == []:
            metadataDict, "Please check at least one box indicating the species."

        return metadataDict, ""
    
    # Filters series based on the user's selections.
    def filter_by_metas(self, metadataDict, fullDataFrame):
        # matchingDataFrame = fullDataFrame.copy(deep=True)

        print(type(metadataDict["Start_Year"]))
        fullSeries = fullDataFrame[(fullDataFrame['Samples_Range'].isin(metadataDict["Num_Samples_Range"])) & (fullDataFrame["Year_Released"] >= metadataDict["Start_Year"]) & (fullDataFrame["Year_Released"] <= metadataDict["End_Year"])].index

        experimentTypesDataFrame = pd.read_csv("data/ExperimentTypes_Series.tsv.gz", sep="\t", index_col=0)
        speciesDataFrame = pd.read_csv("data/Species_Series.tsv.gz", sep="\t", index_col=0)

        experimentTypeSeries = experimentTypesDataFrame[experimentTypesDataFrame['Experiment_Type'].isin(metadataDict["Experiment_Types"])].index
        speciesSeries = speciesDataFrame[speciesDataFrame['Species'].isin(metadataDict["Species"])].index

        commonSeries = set(fullSeries) & set(experimentTypeSeries) & set(speciesSeries)

        return commonSeries
    
    # Queries the embedding database based on the closest results to the user IDs input.
    def search_embeddings(self, metaSeries, searchSeries):
        chroma_client = chromadb.PersistentClient(path="data/Embeddings")
        my_collection = chroma_client.get_collection(name="geo_collection")

        embeddings_dict = my_collection.get(ids=searchSeries, include=["embeddings"])
        search_embedding = np.mean(embeddings_dict["embeddings"], axis=0)

        # It returns the search series, so we need to return that many more than the goal amount.
        n_results = 50 + len(searchSeries)
        results = my_collection.query(query_embeddings=search_embedding, n_results=n_results)

        ranked_series = results["ids"][0]

        # Remove the search series.
        for s in searchSeries:
            ranked_series.remove(s)

        return ranked_series

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