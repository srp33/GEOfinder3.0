#user friendly error message with the try-except blocks
def render_error():
    return f"""
    <html>
    <link 
        rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css"
    >
        <body>
            <h1 class="mt-3 subtitle is-3 has-text-centered is-family-sans-serif" id="results">An error occured. Please contact the administrator.</h1>
            <script> 
                results.scrollIntoView({{ behavior: "smooth", block: "start" }});
            </script>
        </body>
    </html>
    """

def invalid_input_msg(bad_format_ids, not_found_ids, valid_ids):
    error_message = "<h3>ERROR:"
    if bad_format_ids:
        error_message += f" Sorry, the following IDs you entered were formatted incorrectly: {', '.join(bad_format_ids)}<br>"
    if not_found_ids:
        error_message +=f" The following IDs you entered were not found in our database: {', '.join(not_found_ids)}<br>"
    if valid_ids:
        error_message +=f" The following IDs you entered were valid: {', '.join(valid_ids)}<br>"
    error_message += "</h3>"
    return error_message

def invalid_year_msg(bad_format_years, not_found_years, valid_years):
    error_message = "<h3>ERROR:"
    if bad_format_years:
        error_message += f" Sorry, the following years you entered were formatted incorrectly: {', '.join(bad_format_years)}<br>"
    if not_found_years:
        error_message +=f" The following years you entered were not found in our database: {', '.join(not_found_years)}<br>Please enter a year within the range 2001-2024.<br>"
    if valid_years:
        error_message +=f" The following years you entered were valid: {', '.join(valid_years)}<br>"
    error_message += "</h3>"
    return error_message

def experiment_error_msg():
    return f"<h3>ERROR: Please select one or more experiment types.</h3><br>"

def num_samples_error_msg ():
    return f"<h3>ERROR: Please select a range for number of samples.</h3><br>"