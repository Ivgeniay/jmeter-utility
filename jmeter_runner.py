import subprocess
import tempfile
import os
import uuid
import csv
from urllib.parse import urlparse
from models import JMeterResult, Request, Record, TransactionGroup
from console import Log, NullLog


SIMPLE_DATA_WRITER_TEMPLATE = '''<ResultCollector guiclass="SimpleDataWriter" testclass="ResultCollector" testname="__temp_data_writer__" enabled="true">
  <boolProp name="ResultCollector.error_logging">false</boolProp>
  <objProp>
    <name>saveConfig</name>
    <value class="SampleSaveConfiguration">
      <time>true</time>
      <latency>true</latency>
      <timestamp>true</timestamp>
      <success>true</success>
      <label>true</label>
      <code>true</code>
      <message>true</message>
      <threadName>true</threadName>
      <dataType>true</dataType>
      <encoding>false</encoding>
      <assertions>true</assertions>
      <subresults>true</subresults>
      <responseData>false</responseData>
      <samplerData>false</samplerData>
      <xml>false</xml>
      <fieldNames>true</fieldNames>
      <responseHeaders>false</responseHeaders>
      <requestHeaders>false</requestHeaders>
      <responseDataOnError>false</responseDataOnError>
      <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
      <assertionsResultsToSave>0</assertionsResultsToSave>
      <bytes>true</bytes>
      <sentBytes>true</sentBytes>
      <url>true</url>
      <threadCounts>true</threadCounts>
      <idleTime>true</idleTime>
      <connectTime>true</connectTime>
    </value>
  </objProp>
  <stringProp name="filename">{csv_path}</stringProp>
</ResultCollector>
<hashTree/>
'''


def get_temp_dir(log: Log) -> str:
    try:
        temp_dir = tempfile.gettempdir()
        test_file = os.path.join(temp_dir, f'test_{uuid.uuid4().hex}')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        log.log(f'Using system temp directory: {temp_dir}')
        return temp_dir
    except Exception as e:
        fallback = os.getcwd()
        log.log(f'System temp not available ({e}), using: {fallback}')
        return fallback


def inject_data_writer(content: str, csv_path: str) -> str:
    writer_xml = SIMPLE_DATA_WRITER_TEMPLATE.format(csv_path=csv_path)
    
    last_pos = content.rfind('</hashTree>')
    if last_pos == -1:
        raise ValueError('Invalid JMX file: no closing </hashTree> found')
    
    second_last_pos = content.rfind('</hashTree>', 0, last_pos)
    if second_last_pos == -1:
        raise ValueError('Invalid JMX file: structure error - need at least 2 </hashTree> tags')
    
    new_content = content[:second_last_pos] + writer_xml + '\n' + content[second_last_pos:]
    
    return new_content


def remove_data_writer(content: str) -> str:
    import re
    
    pattern = r'<ResultCollector[^>]*testname="__temp_data_writer__"[^>]*>.*?</ResultCollector>\s*<hashTree/>'
    new_content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    return new_content


def run_jmeter(jmeter_path: str, jmx_path: str) -> tuple[int, str, str]:
    cmd = [
        jmeter_path,
        '-n',
        '-t', jmx_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return result.returncode, result.stdout, result.stderr


def parse_jtl_csv(csv_path: str, log: Log) -> JMeterResult:
    result = JMeterResult()
    current_transaction_requests = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            url = row.get('URL', '')
            label = row.get('label', '')
            
            if url == 'null' or url == '':
                transaction = TransactionGroup(
                    name=label,
                    requests=current_transaction_requests.copy()
                )
                result.transactions.append(transaction)
                current_transaction_requests = []
                log.log(f'Transaction completed: {label} ({len(transaction.requests)} requests)')
                continue
            
            method = ''
            path = ''
            
            # Основной запрос — label содержит метод и path
            if ' ' in label and not label.startswith('http'):
                parts = label.split(' ', 1)
                if parts[0] in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    method = parts[0]
                    path = parts[1]
            
            # Embedded/redirect — label это URL, берём path из URL колонки
            if not method:
                method = 'GET'
                parsed_url = urlparse(url)
                path = parsed_url.path
            
            query_string = []
            parsed_url = urlparse(url)
            if parsed_url.query:
                for param in parsed_url.query.split('&'):
                    if '=' in param:
                        name, value = param.split('=', 1)
                        query_string.append(Record(name=name, value=value))
                    else:
                        query_string.append(Record(name=param, value=''))
            
            request = Request(
                method=method,
                url=path,
                http_version='',
                query_string=query_string,
                headers_size=int(row.get('bytes', 0)),
                body_size=int(row.get('sentBytes', 0))
            )
            
            result.all_requests.append(request)
            current_transaction_requests.append(request)
    
    log.log(f'Total: {len(result.all_requests)} requests in {len(result.transactions)} transactions')
    return result

# def parse_jtl_csv(csv_path: str, log: Log) -> JMeterResult:
#     result = JMeterResult()
#     current_transaction_requests = []
    
#     with open(csv_path, 'r', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
        
#         for row in reader:
#             url = row.get('URL', '')
#             label = row.get('label', '')
            
#             if url == 'null' or url == '':
#                 transaction = TransactionGroup(
#                     name=label,
#                     requests=current_transaction_requests.copy()
#                 )
#                 result.transactions.append(transaction)
#                 current_transaction_requests = []
#                 log.log(f'Transaction completed: {label} ({len(transaction.requests)} requests)')
#                 continue
            
#             parsed_url = urlparse(url)
#             path = parsed_url.path
            
#             method = ''
#             if ' ' in label:
#                 parts = label.split(' ', 1)
#                 if parts[0] in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
#                     method = parts[0]
            
#             if not method:
#                 method = 'GET'
            
#             query_string = []
#             if parsed_url.query:
#                 for param in parsed_url.query.split('&'):
#                     if '=' in param:
#                         name, value = param.split('=', 1)
#                         query_string.append(Record(name=name, value=value))
#                     else:
#                         query_string.append(Record(name=param, value=''))
            
#             request = Request(
#                 method=method,
#                 url=path,
#                 http_version='',
#                 query_string=query_string,
#                 headers_size=int(row.get('bytes', 0)),
#                 body_size=int(row.get('sentBytes', 0))
#             )
            
#             result.all_requests.append(request)
#             current_transaction_requests.append(request)
    
#     log.log(f'Total: {len(result.all_requests)} requests in {len(result.transactions)} transactions')
#     return result


def run_and_collect(jmeter_path: str, jmx_path: str, log: Log | None = None) -> list[Request]:
    if log is None:
        log = NullLog()
    
    temp_dir = get_temp_dir(log)
    unique_id = uuid.uuid4().hex
    
    temp_jmx_path = os.path.join(temp_dir, f'temp_{unique_id}.jmx')
    temp_csv_path = os.path.join(temp_dir, f'results_{unique_id}.csv')
    
    try:
        with open(jmx_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        modified_content = inject_data_writer(original_content, temp_csv_path)
        
        with open(temp_jmx_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        log.log(f'Temp JMX created: {temp_jmx_path}')
        log.log(f'Temp CSV target: {temp_csv_path}')
        log.log(f'Running JMeter: {jmeter_path} -n -t {temp_jmx_path}')
        
        returncode, stdout, stderr = run_jmeter(jmeter_path, temp_jmx_path)
        
        if stdout:
            log.log(f'JMeter stdout:\n{stdout}')
        if stderr:
            log.log(f'JMeter stderr:\n{stderr}')
        
        if returncode != 0:
            raise RuntimeError(f'JMeter failed with code {returncode}: {stderr}')
        
        if not os.path.exists(temp_csv_path):
            raise RuntimeError(f'JMeter did not create results file: {temp_csv_path}')
        
        requests = parse_jtl_csv(temp_csv_path, log)
        
        return requests
    
    finally:
        if os.path.exists(temp_jmx_path):
            os.remove(temp_jmx_path)
            log.log(f'Removed temp JMX: {temp_jmx_path}')
        
        if os.path.exists(temp_csv_path):
            os.remove(temp_csv_path)
            log.log(f'Removed temp CSV: {temp_csv_path}')