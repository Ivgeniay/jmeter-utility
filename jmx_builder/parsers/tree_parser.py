from abc import ABC, abstractmethod
import re
from jmx_builder.models.tree import TreeElement

class TreeElementParser(ABC):
    @staticmethod
    @abstractmethod
    def parse(xml_content: str) -> TreeElement:
        pass

class TreeParser:
    def __init__(self):
        self._parsers: dict[str, type] = {}
    
    def register_parser(self, tag_name: str, parser_class: type) -> None:
        self._parsers[tag_name] = parser_class
    
    def parse(self, xml: str) -> TreeElement | list[TreeElement]:
        content = xml.strip()
        
        jmeter_match = re.search(r'<jmeterTestPlan[^>]*>(.*)</jmeterTestPlan>', content, re.DOTALL)
        if jmeter_match:
            content = jmeter_match.group(1).strip()
        
        hashtree_content = self.extract_hashtree_content(content)
        if hashtree_content is not None:
            content = hashtree_content
        
        elements = self.parse_hashtree(content)
        
        if len(elements) == 1:
            return elements[0]
        
        return elements
    
    def extract_hashtree_content(self, content: str) -> str | None:
        content = content.strip()
        
        if not content.startswith('<hashTree>'):
            return None
        
        depth = 1
        pos = len('<hashTree>')
        inner_start = pos
        
        while depth > 0 and pos < len(content):
            next_open = content.find('<hashTree>', pos)
            next_close = content.find('</hashTree>', pos)
            next_self = content.find('<hashTree/>', pos)
            
            candidates = []
            if next_open != -1:
                candidates.append((next_open, 'open'))
            if next_close != -1:
                candidates.append((next_close, 'close'))
            if next_self != -1:
                candidates.append((next_self, 'self'))
            
            if not candidates:
                return None
            
            candidates.sort(key=lambda x: x[0])
            nearest_pos, nearest_type = candidates[0]
            
            if nearest_type == 'open':
                depth += 1
                pos = nearest_pos + len('<hashTree>')
            elif nearest_type == 'close':
                depth -= 1
                if depth == 0:
                    return content[inner_start:nearest_pos].strip()
                pos = nearest_pos + len('</hashTree>')
            else:
                pos = nearest_pos + len('<hashTree/>')
        
        return None
    
    def parse_hashtree(self, hashtree_content: str) -> list[TreeElement]:
        elements = []
        pos = 0
        
        while pos < len(hashtree_content):
            hashtree_content_stripped = hashtree_content[pos:].strip()
            if not hashtree_content_stripped:
                break
            
            pos = len(hashtree_content) - len(hashtree_content_stripped)
            
            tag_match = re.match(r'<(\w+)\s', hashtree_content[pos:])
            if not tag_match:
                break
            
            tag_name = tag_match.group(1)
            
            element_xml, element_end = self.extract_element(hashtree_content, pos, tag_name)
            pos = element_end
            
            children_hashtree, hashtree_end = self.extract_hashtree(hashtree_content, pos)
            pos = hashtree_end
            
            parser_class = self._parsers.get(tag_name)
            if not parser_class:
                raise ValueError(f"No parser registered for tag: {tag_name}")
            
            element = parser_class.parse(element_xml)
            
            if children_hashtree:
                children = self.parse_hashtree(children_hashtree)
                for child in children:
                    element.add_child(child)
            
            elements.append(element)
        
        return elements
    
    def extract_element(self, content: str, start: int, tag_name: str) -> tuple[str, int]:
        end_tag = f'</{tag_name}>'
        end_pos = content.find(end_tag, start)
        if end_pos == -1:
            raise ValueError(f"No closing tag for {tag_name}")
        end_pos += len(end_tag)
        return content[start:end_pos], end_pos
    
    def extract_hashtree(self, content: str, start: int) -> tuple[str, int]:
        remaining = content[start:].strip()
        if not remaining:
            raise ValueError(f"Expected <hashTree> at position {start}, got end of content")
        
        actual_start = start + (len(content[start:]) - len(content[start:].lstrip()))
        
        if remaining.startswith('<hashTree/>'):
            return "", actual_start + len('<hashTree/>')
        
        if remaining.startswith('<hashTree>'):
            depth = 1
            pos = actual_start + len('<hashTree>')
            inner_start = pos
            
            while depth > 0 and pos < len(content):
                next_open = content.find('<hashTree>', pos)
                next_close = content.find('</hashTree>', pos)
                next_self = content.find('<hashTree/>', pos)
                
                candidates = []
                if next_open != -1:
                    candidates.append((next_open, 'open'))
                if next_close != -1:
                    candidates.append((next_close, 'close'))
                if next_self != -1:
                    candidates.append((next_self, 'self'))
                
                if not candidates:
                    raise ValueError("Unclosed <hashTree>")
                
                candidates.sort(key=lambda x: x[0])
                nearest_pos, nearest_type = candidates[0]
                
                if nearest_type == 'open':
                    depth += 1
                    pos = nearest_pos + len('<hashTree>')
                elif nearest_type == 'close':
                    depth -= 1
                    if depth == 0:
                        return content[inner_start:nearest_pos].strip(), nearest_pos + len('</hashTree>')
                    pos = nearest_pos + len('</hashTree>')
                else:
                    pos = nearest_pos + len('<hashTree/>')
            
            raise ValueError("Unclosed <hashTree>")
        
        raise ValueError(f"Expected <hashTree> at position {start}, got: {remaining[:50]}")