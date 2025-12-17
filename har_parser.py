import json
from urllib.parse import urlparse
from models import (
    Request, Record, Cookie, PostData
)


def parse_har(filepath: str) -> list[Request]:
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        har = json.load(f)
    
    requests = []
    
    for entry in har['log']['entries']:
        req = entry['request']
        
        parsed_url = urlparse(req['url'])
        path = parsed_url.path
        
        headers = [
            Record(name=h['name'], value=h['value'], comment=h.get('comment', ''))
            for h in req.get('headers', [])
        ]
        
        cookies = [
            Cookie(
                name=c['name'],
                value=c['value'],
                path=c.get('path', ''),
                domain=c.get('domain', ''),
                expires=c.get('expires', ''),
                http_only=c.get('httpOnly', False),
                secure=c.get('secure', False),
                comment=c.get('comment', '')
            )
            for c in req.get('cookies', [])
        ]
        
        query_string = [
            Record(name=q['name'], value=q['value'], comment=q.get('comment', ''))
            for q in req.get('queryString', [])
        ]
        
        post_data = None
        if 'postData' in req:
            pd = req['postData']
            params = [
                Record(
                    name=p['name'],
                    value=p.get('value', ''),
                    comment=p.get('comment', '')
                )
                for p in pd.get('params', [])
            ]
            post_data = PostData(
                mime_type=pd.get('mimeType', ''),
                text=pd.get('text', ''),
                params=params,
                comment=pd.get('comment', '')
            )
        
        request = Request(
            method=req['method'],
            url=path,
            http_version=req.get('httpVersion', ''),
            cookies=cookies,
            headers=headers,
            query_string=query_string,
            post_data=post_data,
            headers_size=req.get('headersSize', 0),
            body_size=req.get('bodySize', 0),
            comment=req.get('comment', '')
        )
        
        requests.append(request)
    
    return requests