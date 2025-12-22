from enum import Enum
from typing import Callable
from jmx_builder.models.tree import JMeterTestPlan, TreeElement
from jmx_builder.utility.search import search_elements


def print_tree(root: TreeElement | JMeterTestPlan, indent: str = "", is_last: bool = True) -> str:
    connector = "└── " if is_last else "├── "
    result = indent + connector + root.testname + "\n"
    
    indent += "    " if is_last else "│   "
    
    for i, child in enumerate(root.children):
        is_last_child = (i == len(root.children) - 1)
        result += print_tree(child, indent, is_last_child)
    
    return result

def print_path(root: TreeElement | JMeterTestPlan, target: TreeElement) -> str | None:
    if isinstance(root, JMeterTestPlan):
        rootName = 'Root'
    else:
        rootName = root.testname
    
    if root.guid == target.guid:
        return rootName
    
    for child in root.children:
        child_path = print_path(child, target)
        if child_path is not None:
            return rootName + " -> " + child_path
    
    return None

def print_paths(root: TreeElement | JMeterTestPlan, predicate: Callable[[TreeElement], bool]) -> list[str]:
    elements = search_elements(root, predicate, include_root=True)
    
    result: list[str] = []
    for element in elements:
        path = print_path(root, element)
        if path is not None:
            result.append(path)
    
    return result