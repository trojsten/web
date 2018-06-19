# -*- coding: utf-8 -*-
import re

FIELD_SEARCH_PATTERN = re.compile(r'\{(\w+)\}')
FIELD_REPLACE_PATTERN = '{{{}}}'
