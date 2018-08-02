import os
import sys
def html_parse(template,project_id,issue_id,title,description,project_name,release_tag):
    html_string = open(template,'r').read()
    html_new = html_string.replace("""{{project_id}}""",project_id)
    html_new = html_new.replace("""{{jira_issue_id}}""",issue_id)
    html_new = html_new.replace("""{{jira_title}}""",title)
    html_new = html_new.replace("""{{customer_description}}""",description)
    html_new = html_new.replace("""{{project_name}}""",project_name)
    html_new = html_new.replace("""{{release_tag}}""",release_tag)
    return html_new


