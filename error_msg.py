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
    error_message = f'''<h3>ERROR:'''
    if bad_format_ids:
        error_message += f'''<div class="error-message">Sorry, the following IDs you entered were formatted incorrectly: {', '.join(bad_format_ids)}</div>'''
    if not_found_ids:
        error_message +=f'''<div class="error-message">The following IDs you entered are currently not supported by our database: {', '.join(not_found_ids)}<br>This could be because the GEO accession number is invalid, or that dataset is currently not included in GEOfinder.</div>'''
    if valid_ids:
        error_message +=f'''<div class="valid-message">The following IDs you entered were valid: {', '.join(valid_ids)}</div>'''
    error_message += f'''</h3>'''
    return error_message

def invalid_year_msg(bad_format_years, not_found_years, valid_years):
    error_message = f'''<h3>ERROR:'''
    if bad_format_years:
        error_message += f'''<div class="error-message">Sorry, the following years you entered were formatted incorrectly: {', '.join(bad_format_years)}</div>'''
    if not_found_years:
        error_message +=f'''<div class="error-message">The following years you entered were not supported by our database: {', '.join(not_found_years)}<br>Please enter a year within the range 2001-2024.</div>'''
    if valid_years:
        error_message +=f'''<div class="valid-message">The following years you entered were valid: {', '.join(valid_years)}</div>'''
    error_message += f'''</h3>'''
    return error_message

def checkbox_error_msg():
    return f'''<h3>ERROR: Please check at least one box for each filter category.</h3><br>'''