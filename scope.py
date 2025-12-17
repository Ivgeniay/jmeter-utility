from dataclasses import dataclass
import re


@dataclass
class ScopeResult:
    found: bool = False
    content: str = ""
    start_line: int = 0
    end_line: int = 0

def extract_scope_by_element_name(content: str, element_name: str) -> ScopeResult:
    result = ScopeResult()
    
    element_regex = rf'<[^>]+testname="{re.escape(element_name)}"[^>]*>'
    element_match = re.search(element_regex, content)
    
    if not element_match:
        return result
    
    hashtree_start_regex = r'<hashTree[^/>]*>'
    hashtree_match = re.search(hashtree_start_regex, content[element_match.end():])
    
    if not hashtree_match:
        return result
    
    start_pos = element_match.end() + hashtree_match.start()
    pos = element_match.end() + hashtree_match.end()
    depth = 1
    
    open_tag = re.compile(r'<hashTree[^/>]*>')
    close_tag = re.compile(r'</hashTree>')
    self_closing = re.compile(r'<hashTree\s*/>')
    
    while depth > 0 and pos < len(content):
        open_match = open_tag.search(content, pos)
        close_match = close_tag.search(content, pos)
        self_match = self_closing.search(content, pos)
        
        matches = []
        if open_match:
            matches.append(('open', open_match.start(), open_match.end()))
        if close_match:
            matches.append(('close', close_match.start(), close_match.end()))
        if self_match:
            matches.append(('self', self_match.start(), self_match.end()))
        
        if not matches:
            return result
        
        matches.sort(key=lambda x: x[1])
        tag_type, tag_start, tag_end = matches[0]
        
        if tag_type == 'open':
            depth += 1
        elif tag_type == 'close':
            depth -= 1
        
        pos = tag_end
        
        if depth == 0:
            result.found = True
            result.content = content[start_pos:tag_end]
            result.start_pos = start_pos
            result.end_pos = tag_end
    
    return result


