# -*- coding: utf-8 -*-
import re

# probes SVG file for occurrences of strings of form {alphanumericcharacters}
FIELD_SEARCH_PATTERN = re.compile(r'\{(\w+)\}')
# Pattern for replacing the abovementioned strings
FIELD_REPLACE_PATTERN = '{{{field_name}}}'

DIPLOMA_DEFAULT_NAME = 'diploma_joined.pdf'
