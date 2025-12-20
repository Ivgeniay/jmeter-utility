from jmx_builder.models.tree import TreeElement
from abc import ABC, abstractmethod
import re


class TreeElementParser(ABC):
    @staticmethod
    @abstractmethod
    def parse(xml_content: str) -> TreeElement:
        pass
    
    @staticmethod
    def extract_attribute(xml_content: str, attr_name: str) -> str | None:
        match = re.search(rf'{attr_name}="([^"]*)"', xml_content)
        return match.group(1) if match else None
    
    @staticmethod
    def extract_simple_prop_value(xml_content: str, prop_name: str) -> str | None:
        """Извлекает значение простого пропа (stringProp, boolProp, intProp, longProp)"""
        pattern = rf'<(?:stringProp|boolProp|intProp|longProp)\s+name="{prop_name}"[^>]*>([^<]*)</(?:stringProp|boolProp|intProp|longProp)>'
        match = re.search(pattern, xml_content)
        return match.group(1) if match else None
    
    @staticmethod
    def extract_element_prop_content(xml_content: str, prop_name: str) -> str | None:
        """Извлекает содержимое elementProp (всё между открывающим и закрывающим тегом)"""
        import re
        
        open_pattern = rf'<elementProp\s+name="{prop_name}"[^>]*>'
        open_match = re.search(open_pattern, xml_content)
        if not open_match:
            return None
        
        start_pos = open_match.end()
        pos = start_pos
        depth = 1
        
        while depth > 0 and pos < len(xml_content):
            next_open = xml_content.find('<elementProp', pos)
            next_close = xml_content.find('</elementProp>', pos)
            next_self = re.search(r'<elementProp[^>]*/>', xml_content[pos:])
            next_self_pos = pos + next_self.start() if next_self else -1
            
            candidates = []
            if next_open != -1:
                candidates.append((next_open, 'open'))
            if next_close != -1:
                candidates.append((next_close, 'close'))
            if next_self_pos != -1:
                candidates.append((next_self_pos, 'self'))
            
            if not candidates:
                return None
            
            candidates.sort(key=lambda x: x[0])
            nearest_pos, nearest_type = candidates[0]
            
            if nearest_type == 'open':
                depth += 1
                pos = nearest_pos + len('<elementProp')
            elif nearest_type == 'close':
                depth -= 1
                if depth == 0:
                    return xml_content[start_pos:nearest_pos].strip()
                pos = nearest_pos + len('</elementProp>')
            else:
                pos = next_self_pos + next_self.end() - next_self.start()
        
        return None
    
    @staticmethod
    def extract_collection_prop_content(xml_content: str, prop_name: str) -> str | None:
        """Извлекает содержимое collectionProp (всё между открывающим и закрывающим тегом)"""
        import re
        
        self_closing = rf'<collectionProp\s+name="{prop_name}"[^>]*/>'
        if re.search(self_closing, xml_content):
            return ""
        
        open_pattern = rf'<collectionProp\s+name="{prop_name}"[^>]*>'
        open_match = re.search(open_pattern, xml_content)
        if not open_match:
            return None
        
        start_pos = open_match.end()
        pos = start_pos
        depth = 1
        
        while depth > 0 and pos < len(xml_content):
            next_open = xml_content.find('<collectionProp', pos)
            next_close = xml_content.find('</collectionProp>', pos)
            next_self = re.search(r'<collectionProp[^>]*/>', xml_content[pos:])
            next_self_pos = pos + next_self.start() if next_self else -1
            
            candidates = []
            if next_open != -1:
                candidates.append((next_open, 'open'))
            if next_close != -1:
                candidates.append((next_close, 'close'))
            if next_self_pos != -1:
                candidates.append((next_self_pos, 'self'))
            
            if not candidates:
                return None
            
            candidates.sort(key=lambda x: x[0])
            nearest_pos, nearest_type = candidates[0]
            
            if nearest_type == 'open':
                depth += 1
                pos = nearest_pos + len('<collectionProp')
            elif nearest_type == 'close':
                depth -= 1
                if depth == 0:
                    return xml_content[start_pos:nearest_pos].strip()
                pos = nearest_pos + len('</collectionProp>')
            else:
                pos = next_self_pos + next_self.end() - next_self.start()
        
        return None
    
    @staticmethod
    def is_prop_exists(xml_content: str, prop_name: str) -> bool:
        """Проверяет существование пропа по имени"""
        pattern = rf'name="{prop_name}"'
        return bool(re.search(pattern, xml_content))
