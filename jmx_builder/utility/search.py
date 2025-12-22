from typing import Callable
from jmx_builder.models.tree import JMeterTestPlan, TreeElement


def search_element(root: TreeElement | JMeterTestPlan, predicate: Callable[[TreeElement], bool], include_root: bool = False) -> TreeElement | None:
    if include_root and not isinstance(root, JMeterTestPlan) and predicate(root):
        return root
    
    for child in root.children:
        if predicate(child):
            return child
        
        result = search_element(child, predicate)
        if result is not None:
            return result
    
    return None

def search_elements(root: TreeElement | JMeterTestPlan, predicate: Callable[[TreeElement], bool], include_root: bool = False) -> list[TreeElement]:
    result_list: list[TreeElement] = []
    
    if include_root and not isinstance(root, JMeterTestPlan) and predicate(root):
        result_list.append(root)
    
    for child in root.children:
        if predicate(child):
            result_list.append(child)

        res = search_elements(child, predicate, include_root=False)
        result_list.extend(res)
    
    return result_list