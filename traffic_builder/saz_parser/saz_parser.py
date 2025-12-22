import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Optional

from traffic_builder.saz_parser.models import (
    SazArchive, SazSession, SessionMetadata, SessionTimers,
    PipeInfo, SessionFlag, Request, Response, RequestLine,
    StatusLine, Header
)


def _parse_datetime(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str).astimezone().astimezone(None).replace(tzinfo=None)


def _parse_metadata(xml_content: str) -> SessionMetadata:
    root = ET.fromstring(xml_content)
    
    sid = int(root.attrib.get('SID', 0))
    bit_flags = int(root.attrib.get('BitFlags', 0))
    
    timers_elem = root.find('SessionTimers')
    timers = SessionTimers(
        client_connected=_parse_datetime(timers_elem.attrib['ClientConnected']),
        client_begin_request=_parse_datetime(timers_elem.attrib['ClientBeginRequest']),
        got_request_headers=_parse_datetime(timers_elem.attrib['GotRequestHeaders']),
        client_done_request=_parse_datetime(timers_elem.attrib['ClientDoneRequest']),
        server_connected=_parse_datetime(timers_elem.attrib['ServerConnected']),
        fiddler_begin_request=_parse_datetime(timers_elem.attrib['FiddlerBeginRequest']),
        server_got_request=_parse_datetime(timers_elem.attrib['ServerGotRequest']),
        server_begin_response=_parse_datetime(timers_elem.attrib['ServerBeginResponse']),
        got_response_headers=_parse_datetime(timers_elem.attrib['GotResponseHeaders']),
        server_done_response=_parse_datetime(timers_elem.attrib['ServerDoneResponse']),
        client_begin_response=_parse_datetime(timers_elem.attrib['ClientBeginResponse']),
        client_done_response=_parse_datetime(timers_elem.attrib['ClientDoneResponse']),
        gateway_time=int(timers_elem.attrib.get('GatewayTime', 0)),
        dns_time=int(timers_elem.attrib.get('DNSTime', 0)),
        tcp_connect_time=int(timers_elem.attrib.get('TCPConnectTime', 0)),
        https_handshake_time=int(timers_elem.attrib.get('HTTPSHandshakeTime', 0))
    )
    
    pipe_info_elem = root.find('PipeInfo')
    pipe_info = PipeInfo(
        clt_reuse=pipe_info_elem.attrib.get('CltReuse', 'false').lower() == 'true',
        reused=pipe_info_elem.attrib.get('Reused', 'false').lower() == 'true'
    )
    
    flags = []
    flags_elem = root.find('SessionFlags')
    if flags_elem is not None:
        for flag_elem in flags_elem.findall('SessionFlag'):
            flags.append(SessionFlag(
                name=flag_elem.attrib.get('N', ''),
                value=flag_elem.attrib.get('V', '')
            ))
    
    return SessionMetadata(
        sid=sid,
        bit_flags=bit_flags,
        timers=timers,
        pipe_info=pipe_info,
        flags=flags
    )


def _parse_http_headers(lines: list[str]) -> list[Header]:
    headers = []
    for line in lines:
        if ':' in line:
            name, value = line.split(':', 1)
            headers.append(Header(name=name.strip(), value=value.strip()))
    return headers


def _parse_request(content: bytes) -> Request:
    text = content.decode('utf-8', errors='ignore')
    lines = text.split('\n')
    
    request_line_parts = lines[0].strip().split(' ', 2)
    request_line = RequestLine(
        method=request_line_parts[0],
        url=request_line_parts[1],
        http_version=request_line_parts[2] if len(request_line_parts) > 2 else 'HTTP/1.1'
    )
    
    header_end = 0
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '':
            header_end = i
            break
    
    headers = _parse_http_headers(lines[1:header_end])
    
    body = b''
    if header_end < len(lines) - 1:
        body_text = '\n'.join(lines[header_end + 1:])
        body = body_text.encode('utf-8')
    
    return Request(
        request_line=request_line,
        headers=headers,
        body=body
    )


def _parse_response(content: bytes) -> Response:
    text = content.decode('utf-8', errors='ignore')
    lines = text.split('\n')
    
    status_line_parts = lines[0].strip().split(' ', 2)
    status_line = StatusLine(
        http_version=status_line_parts[0],
        status_code=int(status_line_parts[1]),
        status_text=status_line_parts[2] if len(status_line_parts) > 2 else ''
    )
    
    header_end = 0
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '':
            header_end = i
            break
    
    headers = _parse_http_headers(lines[1:header_end])
    
    body = b''
    if header_end < len(lines) - 1:
        body_text = '\n'.join(lines[header_end + 1:])
        body = body_text.encode('utf-8')
    
    return Response(
        status_line=status_line,
        headers=headers,
        body=body
    )


def parse_saz(filepath: str | Path) -> SazArchive:
    archive = SazArchive()
    
    with zipfile.ZipFile(filepath, 'r') as zf:
        file_list = zf.namelist()
        
        session_numbers = set()
        for name in file_list:
            if name.startswith('raw/') and '_m.xml' in name:
                num = name.split('/')[-1].split('_')[0]
                session_numbers.add(num)
        
        for num in sorted(session_numbers):
            metadata_file = f'raw/{num}_m.xml'
            request_file = f'raw/{num}_c.txt'
            response_file = f'raw/{num}_s.txt'
            
            metadata = None
            request = None
            response = None
            
            if metadata_file in file_list:
                xml_content = zf.read(metadata_file).decode('utf-8')
                metadata = _parse_metadata(xml_content)
            
            if request_file in file_list:
                request_content = zf.read(request_file)
                request = _parse_request(request_content)
            
            if response_file in file_list:
                response_content = zf.read(response_file)
                response = _parse_response(response_content)
            
            if metadata and request and response:
                session = SazSession(
                    session_id=metadata.sid,
                    metadata=metadata,
                    request=request,
                    response=response
                )
                archive.sessions.append(session)
    
    return archive


def get_sessions(archive: SazArchive) -> list[SazSession]:
    return archive.sessions


def get_sessions_by_status(archive: SazArchive, status_code: int) -> list[SazSession]:
    return [s for s in archive.sessions if s.response.status_line.status_code == status_code]


def get_sessions_by_method(archive: SazArchive, method: str) -> list[SazSession]:
    return [s for s in archive.sessions if s.request.request_line.method.upper() == method.upper()]


def get_sessions_by_flag(archive: SazArchive, flag_name: str, flag_value: Optional[str] = None) -> list[SazSession]:
    result = []
    for session in archive.sessions:
        for flag in session.metadata.flags:
            if flag.name == flag_name:
                if flag_value is None or flag.value == flag_value:
                    result.append(session)
                    break
    return result