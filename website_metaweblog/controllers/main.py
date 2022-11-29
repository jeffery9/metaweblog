import requests
import json
from odoo.addons.portal.controllers.web import Home

class Website(Home):

    @http.route(['/website/seo_suggest'], type='json', auth="user", website=True)
    def seo_suggest(self, keywords=None, lang=None):
        language = lang.split("_")
        url = "http://suggestion.baidu.com/su"
        try:
            req = requests.get(url, params={
                'action': 'opensearch', 'wd': keywords, })
            req.raise_for_status()
            response = req.text
        except IOError:
            return []
        data = json.loads(response)
        return json.dumps(data[1])