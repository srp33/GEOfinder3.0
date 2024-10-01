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


def invalid_input_msg(bad_format_ids, not_found_ids, valid_ids, bad_format_years, not_found_years, valid_years):
    error_message = ""
    if bad_format_ids:
        error_message += f"<tr><td>Sorry, the following IDs you entered were formatted incorrectly: {', '.join(bad_format_ids)}</td></tr>"
    if not_found_ids:
        error_message +=f"<tr><td>The following IDs you entered were not found in our database: {', '.join(not_found_ids)}</td></tr>"
    if valid_ids:
        error_message +=f"<tr><td>The following IDs you entered were valid: {', '.join(valid_ids)}</td></tr>"
    if bad_format_years:
        error_message += f"<tr><td>Sorry, the following years you entered were formatted incorrectly: {', '.join(bad_format_years)}</td></tr>"
    if not_found_years:
        error_message +=f"<tr><td>The following years you entered were not found in our database: {', '.join(not_found_years)}</td></tr>"
    if valid_years:
        error_message +=f"<tr><td>The following years you entered were valid: {', '.join(valid_years)}</td></tr>"
    return error_message