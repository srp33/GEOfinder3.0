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
    def __init__(self):
        print("Initializing...")
        self.df = pd.read_csv("data/FilteredGEO.tsv.gz", sep="\t", index_col=0).fillna('')

        chroma_client = chromadb.PersistentClient(path="data/Embeddings")
        self.embedding_db = chroma_client.get_collection(name="geo_collection")

        self.num_samples_options = ["1-10", "11-50", "51-100", "101-500", "501-1000", "1000+"]

        self.experiment_types = []
        with gzip.open("data/ExperimentTypes.tsv.gz") as expTypesFile:
            for line in expTypesFile:
                self.experiment_types.append(line.decode().rstrip("\n"))

        self.species = []
        with gzip.open("data/Species.tsv.gz") as speciesFile:
            for line in speciesFile:
                self.species.append(line.decode().rstrip("\n"))

        self.earliest_start_year = 2001
        self.this_year = datetime.now().year

        self.MAX_NUM_RESULTS = 100

    @cherrypy.expose
    def index(self):
        try:
            return self.header() + self.search_home() + self.footer()
        except:
            error = self.format_error_msg(traceback.format_exc())
            return self.header() + error + self.footer()

    @cherrypy.expose
    def about(self):
        try:
            return self.header() + self.read_text_file("htmlFiles/about.html") + self.footer()
        except:
            error = self.format_error_msg(traceback.format_exc())
            return self.header() + error + self.footer()

    @cherrypy.expose
    def query(self, searchSeries, checkboxDict, startYear, endYear):
        try:
            # This should be robust to extract characters, inconsistent capitalization, etc.
            searchSeries = re.findall(r'GSE\d{1,8}', searchSeries, re.IGNORECASE)
            searchSeries = [id.upper() for id in searchSeries]

            if len(searchSeries) == 0:
                return self.format_error_msg("No valid accession identifiers were provided.")

            not_found_ids = self.validate_ids(searchSeries)
            if len(not_found_ids) > 0:
                return self.format_error_msg(f'''The following ID(s) you entered are currently not available in GEOfinder: {', '.join(not_found_ids)}. This could be because they are not valid GEO accession number(s) or that we have filtered them for some reason. Please remove the ID(s) from the search box and re-submit.''')
            
            checkboxDict = json.loads(checkboxDict)

            metadataDict, errorMsg = self.make_metadata_dict(checkboxDict, startYear, endYear)

            if len(metadataDict["experiment_types"]) == 0:
                return self.format_error_msg("Please select at least one experiment type.")
            
            if len(metadataDict["species"]) == 0:
                return self.format_error_msg("Please select at least one species.")
            
            if metadataDict["start_year"] > metadataDict["end_year"]:
                return self.format_error_msg("The end year must be later than the start year.")

            if errorMsg != "":
                return self.format_error_msg(errorMsg)

            metaSeries = self.filter_by_metas(metadataDict)

            topSeries = self.search_embeddings(searchSeries, metaSeries, metadataDict)

            return self.generateResultsTable(topSeries)
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
        numSamplesHtml = ""
        for nso in self.num_samples_options:
            numSamplesHtml += f"<div class='field'><label class='checkbox'><input type='checkbox' name='{nso}' value='numSamplesRange' checked> {nso}</label></div>"

        experimentTypesHtml = ""
        for expType in self.experiment_types:
            experimentTypesHtml += f"<div class='field'><label class='checkbox'><input type='checkbox' name='{expType}' value='experimentType' checked /> {expType}</label></div>"

        speciesHtml = ""
        for s in self.species:
            speciesHtml += f"<div class='field'><label class='checkbox'><input type='checkbox' name='{s}' value='species' checked /> {s}</label></div>"

        startYearHtml = f"<option selected>{self.earliest_start_year}</option>\n"
        for year in range(self.earliest_start_year + 1, self.this_year + 1):
            startYearHtml += f"<option>{year}</option>\n"

        endYearHtml = ""
        for year in range(self.earliest_start_year, self.this_year):
            endYearHtml += f"<option>{year}</option>\n"

        endYearHtml += f"<option selected>{self.this_year}</option>"

        return self.read_text_file("htmlFiles/search_home.html").replace("{{ numSamples }}", numSamplesHtml).replace("{{ experimentTypes }}", experimentTypesHtml).replace("{{ species }}", speciesHtml).replace("{{ startYears }}", startYearHtml).replace("{{ endYears }}", endYearHtml)

    def footer(self):
        return self.read_text_file("htmlFiles/footer.html")

    def format_error_msg(self, msg):
        return f"ERROR: {msg}"

    def validate_ids(self, ids):
        not_found_ids = []

        for id in ids:
            if id not in self.df.index:
                not_found_ids.append(id)

        return not_found_ids

    # Return a dictionary containing the user's filter selections.
    def make_metadata_dict(self, checkboxDict, startYear, endYear):
        metadataDict={
            "number_samples_range": [],
            "experiment_types": [],
            "species": [],
            "start_year": int(startYear),
            "end_year": int(endYear)
        }

        for checkboxValue, checkboxCategory in checkboxDict.items():
            if checkboxCategory == "numSamplesRange":
                metadataDict["number_samples_range"].append(checkboxValue)
            elif checkboxCategory == "experimentType":
                metadataDict["experiment_types"].append(checkboxValue)
            elif checkboxCategory == "species":
                metadataDict["species"].append(checkboxValue)

        if metadataDict["number_samples_range"] == []:
            return metadataDict, "Please check at least one box indicating the number of samples per data series."

        if metadataDict["experiment_types"] == []:
            metadataDict, "Please check at least one box indicating the experiment type(s)."

        if metadataDict["species"] == []:
            metadataDict, "Please check at least one box indicating the species."

        return metadataDict, ""

    # Filters series based on the user's selections.
    def filter_by_metas(self, metadataDict):
        df = self.df.copy()

        experimentTypesDF = pd.read_csv("data/ExperimentTypes_Series.tsv.gz", sep="\t", index_col=0)
        speciesDF = pd.read_csv("data/Species_Series.tsv.gz", sep="\t", index_col=0)

        firstSeries = df[(df['Samples_Range'].isin(metadataDict["number_samples_range"])) & (df["Year_Released"] >= metadataDict["start_year"]) & (df["Year_Released"] <= metadataDict["end_year"])].index
        experimentTypeSeries = experimentTypesDF[experimentTypesDF['Experiment_Type'].isin(metadataDict["experiment_types"])].index
        speciesSeries = speciesDF[speciesDF['Species'].isin(metadataDict["species"])].index

        commonSeries = set(firstSeries) & set(experimentTypeSeries) & set(speciesSeries)

        return commonSeries
    
    # Queries the embedding database based on the closest results to the user IDs input.
    def search_embeddings(self, searchSeries, metaSeriesSet, metadataDict):
        embeddingsDict = self.embedding_db.get(ids=searchSeries, include=["embeddings", "metadatas"])
        searchEmbedding = np.mean(embeddingsDict["embeddings"], axis=0)

        # whereDict = {"$and": [{"number_samples_range": {"$in": metadataDict["number_samples_range"]}},
        #                       {"year": {"$gte": metadataDict["start_year"]}},
        #                       {"year": {"$lte": metadataDict["end_year"]}}
        # ]}

        # subWhereDict = {"$or": []}
        # for expType in self.experiment_types:
        #     subWhereDict["$or"].append({expType: {"$eq": expType in metadataDict["experiment_types"]}})
        # whereDict["$and"].append(subWhereDict)

        # subWhereDict = {"$or": []}
        # for s in self.species:
        #     subWhereDict["$or"].append({s: {"$eq": s in metadataDict["species"]}})
        # whereDict["$and"].append(subWhereDict)

        # It returns the search series, so we need to return that many more than the goal amount.
        # nResults = self.MAX_NUM_RESULTS + len(searchSeries)
        # Alternative option: https://github.com/weaviate/weaviate
        # Or Qdrant: https://qdrant.tech/articles/vector-search-filtering/
        results = self.embedding_db.query(
            query_embeddings=searchEmbedding,
            n_results=50000,
            include=["distances"])

        rankedSeries = results["ids"][0]
        # distances = results["distances"][0]

        # Remove the search series.
        # for s in searchSeries:
        #     i = searchSeries.index(s)
        #     del rankedSeries[i]
            # del distances[i]

        topSeries = []

        while len(rankedSeries) > 0 and len(topSeries) < self.MAX_NUM_RESULTS:
            series = rankedSeries.pop(0)
            if series in metaSeriesSet and series not in searchSeries:
                topSeries.append(series)

        return topSeries

        # return rankedSeries, distances

    def generateResultsTable(self, topSeries):
        table = f'''
            <div class="table-container mt-4">
                <div class="title is-3">Top results (up to 100):</div>
                <table class="table is-bordered is-hoverable is-fullwidth">
                    <thead>
                        <tr>
                            <th>GSE ID</th>
                            <th>Title</th>
                            <th>Summary</th>
                            <th>Overall Design</th>
                            <th>Experiment Type(s)</th>
                            <th>Species</th>
                            <th># Samples</th>
                            <th>Year Released</th>
                            <th>Super Series</th>
                            <th>Sub Series</th>
                        </tr>
                    </thead>
                    <tbody>'''

        # The range of this for loop makes it so that the ID that a user is querying on is not included in the results table.
        for id in topSeries:
            row = self.df.loc[id]

            table += '<tr>'

            table += f'''<td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={id}" target="_blank">{id}</a></td> \
                <td>{self.replace_urls(row["Title"])}</td> \
                <td>{self.replace_urls(row["Summary"])}</td> \
                <td>{self.replace_urls(row["Overall_Design"])}</td> \
                <td>{row["Experiment_Type"]}</td> \
                <td>{row["Species"]}</td> \
                <td>{row["Num_Samples"]}</td> \
                <td>{row["Year_Released"]}</td> \
                <td>{row["SuperSeries_GSE"]}</td> \
                <td>{row["SubSeries_GSE"]}</td>'''

            table += '</tr>'
        
        table += f'''</tbody></table></div>'''
        
        return table
    
    def replace_urls(self, text):
        return re.sub(r"(https?:\/\/\S+|www\.\S+)", "[url]", text)

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