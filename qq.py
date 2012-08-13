#!/usr/bin/env python

__all__ = ['qq_download_by_id']

import re
from common import *

def qq_download_by_id(id, title, merge=True):
	url = 'http://vsrc.store.qq.com/%s.flv' % id
	assert title
	download_urls([url], title, 'flv', total_size=None, merge=merge)

