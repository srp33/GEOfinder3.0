# Final Copy
import cherrypy
import re 
import traceback 
import error_msg
import generate_rows_helper
import csv

class WebApp:

    @cherrypy.expose
    def index(self):
        #print(f"\n\n\n dictionary: \n\n\n {simpleDictionary}")
        try:
            return self.top_half_html()
        except:
            with open("error.txt", "w") as error_file:
                traceback.print_exc(file=error_file)
            return error_msg.render_error()

    # a) 1-10, b) 11-50, c) 51-100, d) 101-500, e) 501-1000, f) 1000+
    @cherrypy.expose
    def query(self, ids, human="", mouse="", rat="", a="", b="", c="", d="", e="", f="", rnaSeq="", microarr="", searchType="geoID"):
        #print("\nReceived input:", ids, human, mouse, rat, a, b, c, d, e, f, rnaSeq, microarr)
        #print(f"searchType: {searchType}, type: {type(searchType)}")

        metadata_dct = self.make_metadata_dct([human, mouse, rat], [a, b, c, d, e, f], [rnaSeq, microarr])
        
        print(f"\n\n\nIn query, metadata_dct:{metadata_dct}\n\n\n\n")

        try:
            return self.bottom_half_html(ids, metadata_dct, searchType)
        except:
            with open("error.txt", "w") as error_file:
                traceback.print_exc(file=error_file)
            return error_msg.render_error()

    #Internal:

    def make_metadata_dct(self, species, num_samples, experiment_type):
        metadata_dct={}
        if species:
            metadata_dct["Species"] = [val for val in species if val]
        if num_samples:
            metadata_dct["Num_Samples"] = [val for val in num_samples if val]
        if experiment_type:
            metadata_dct["Experiment_Type"] = [val for val in experiment_type if val]

        return metadata_dct

    def top_half_html(self):
        with open("top_half_html.txt") as top_html:
            html_str = top_html.read()
            return html_str
    
    def bottom_half_html(self, ids, metadata_dct, searchType):
        #print("\n in bottom_half()", ids, metadata_dct, searchType)
        return f"""
        
        <div class="columns is-centered" id="results">
            <div class="columns is-three-quarters">
                <table class="table is-size-medium" id="myTable" border="1">
                    {self.handle_input_ids(ids, metadata_dct, searchType)}
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

    #calls generate_query_results and writes results in html code, to display results in a table 
    def generate_rows(valid_ids=[], words="", metadata_dct={}):
        print("\nGenerate_rows:", valid_ids, words, metadata_dct)

        filtered_df = generate_rows_helper.filter_by_metas(metadata_dct)
        print("filtered df:\n", filtered_df.head())
        
        filtered_ids = filtered_df["GSE"].to_list()
        # print("filtered ids: ", filtered_ids)
        # print("length: ", len(filtered_ids))

        if valid_ids:
            #print("Query by ids...")
            print("***************** about to call generate_id_query_results, valid_ids =", valid_ids)
            results_ids = generate_rows_helper.generate_id_query_results(valid_ids)
        # elif words:
        #     #print("Query by keywords...")
        #     results_ids = generate_rows_helper.generate_keyword_query_results(words)
        else:
            print("\nNo inputs in generate_rows!!\n")
        # print(f"results_ids: {results_ids}")
        
        match_ids = [value for value in results_ids if value in filtered_ids]
        # print("match ids: ", match_ids)


        rows = '<caption class="py-4 mt-3 subtitle is-3 has-text-centered is-family-sans-serif">Relevant Studies:</caption>' + \
                '<tr> <th>GSE ID</th> <th>Summary</th> <th>Species</th> <th># Samples</th> <th>Experiment Type</th></tr>'

        for id in match_ids:

            line = filtered_df[filtered_df["GSE"] == id]

            rows += f'<tr> <td><a href="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={id}">{id}</a></td> \
                <td>{line["Summary"].values[0]}</td> \
                <td>{line["Species"].values[0]}</td> <td>{line["Num_Samples"].values[0]}</td> \
                <td>{line["Experiment_Type"].values[0]}</td> </tr>'

        return rows

    #checks for invalid input, if all input is valid then calls generate_rows 
    def handle_input_ids(self, ids, metadata_dct, searchType):
        print("\nHandle_input_ids:", ids, metadata_dct, searchType)
        
        if (ids == ""):
            return ""
        
        elif searchType=="geoID":

            id_lst = re.split(r"\n|,",ids.strip())
            bad_format_ids = []
            not_found_ids = []   # we no longer have a comprehensive list of ids, to check if id is in our database
            valid_ids = []

            for id in id_lst:
                id = id.strip().upper()

                if not re.search(r"GSE\d+",id):
                    bad_format_ids.append(id)
                # elif id not in database_ids:
                #     not_found_ids.append(id)
                else: 
                    valid_ids.append(id)

            #test values: gse001, gse002, gse789, gse990, jkf292, fif404
            if bad_format_ids or not_found_ids:    
                return '<caption class="py-4 mt-3 subtitle is-3 has-text-centered is-family-sans-serif">ERROR:</caption>' + \
                    error_msg.invalid_id_msg(bad_format_ids, not_found_ids, valid_ids)
            else:
                #print("\nCalling generate rows with ids", valid_ids, metadata_dct)
                return WebApp.generate_rows(valid_ids=valid_ids, metadata_dct=metadata_dct)
 
        elif searchType=="keyword":
            words = ids.strip()
            #print("\nCalling generate rows with keywords", words, metadata_dct)
            return WebApp.generate_rows(words=words, metadata_dct=metadata_dct)

        else:
            print("\nNo inputs in handle_input_ids!!\n")


if __name__ == '__main__':
    cherrypy.quickstart(WebApp(), '/')

'''
6/12
- add in date info and update the experiment type value once we get the tsv file!
- use tsv to create chromadb database (id, emb, metas). One at a time. This one will have less instances for our computer RAM
- next: trying to get the ID's from our collection

- trying to git push but it won't work!

6/13 TO-DO
- X autoscroll down for the error mesage
- X change "human" filter to "homo sapiens"
- make error message replace entire content of the screen?
- left off working on line 268, figuring out avg embeddings/how to implement that now. worked on getting results for a single ID using the real data, 
doing some HTML details 

6/18 to-do
- use notification class for error message, use class "is-hidden" and remove 'is-hidden" if an error occurs. when the user clicks submit, add "is-hidden"
- when we create a collection, see if we can tell it what directory to put it in, if so put it in a collections directory and then put that in the git ignore file
- put the problem into chatgpt "how to completely remove a large file from the history of the git repositroy"
- create one pandas dataframe for each metadata attribute (in the num samples dataframe we'll have to put the num samples into one of our categories)

6/19
- how to query / filtering... if we query first and then filter, we might not get as many results back as the user wants
- test for git to see if it picks up the change im making

6/21
- split code into multiple files for readability
- began to add more species to the checkboxes in top_half_html (currently commented out)

Abby! 
It was a joy working with you! I loved your kindness, generosity, ingenuity, and ability to solve problems.
I hope you have a great day!
Love, Anna :)

9/5
- going through, trying to fix things. first of all, error.txt file is no longer being created, so I can't see what the error is.
- smaller detail that needs to be done - fix javascript so that submit button is functional again once you start typing again, choose other filters, etc. 
- question: line 77?
- did we make a pandas dataframe?
- where to put the allGEO file so that it gets accessed correctly?

9/6
- check make_metadata_dct function - when we don't select any filters, it should return a completely empty dictionary but it really returns {Species:[]...} etc
- check line 134, are the valid id's being checked for whether they are actually found within our database?
- error is in filter_by_metas, check line 79 here to see where things are going wrong 
- where it's breaking: generate_rows_helper, lines 10-11. Issue with make_dataframe function - doesn't print the initial statement even and we don't know why 

9/9 
- issue in make_dataframe, when we are making the species or experiment type dataframe how to handle when there are two types in one ID
- problem is in line 30 of generate_rows_helper - that's where the dataframe breaks and becomes an empty dataframe. need to figure out how to write that line

9/10
- split based on the | in the TSV file before reading them into a dataframe 

'''