from dataclasses import dataclass
from typing import Callable, Iterator
import uuid
from jmx_builder.models.tree import TreeElement, JMeterTestPlan


@dataclass
class TreeNodeInfo:
    element: TreeElement | JMeterTestPlan
    parent: TreeElement | JMeterTestPlan | None
    depth: int
    index: int


class TreeManager:
    def __init__(self, root: TreeElement | JMeterTestPlan):
        self.root = root
        self._cache: dict[str, TreeNodeInfo] = {}
        self._is_dirty = False
        self._build_cache()
    
    def _ensure_cache_valid(self) -> None:
        if self._is_dirty:
            self.rebuild_cache()
    
    def rebuild_cache(self) -> None:
        self._build_cache()
        self._is_dirty = False
    
    def _build_cache(self) -> None:
        self._cache.clear()
        
        if isinstance(self.root, JMeterTestPlan):
            root_guid = id(self.root)
            self._cache[str(root_guid)] = TreeNodeInfo(
                element=self.root,
                parent=None,
                depth=0,
                index=-1
            )
            
            for idx, child in enumerate(self.root.children):
                self._build_cache_recursive(child, self.root, 1, idx)
        else:
            self._cache[self.root.guid] = TreeNodeInfo(
                element=self.root,
                parent=None,
                depth=0,
                index=-1
            )
            
            for idx, child in enumerate(self.root.children):
                self._build_cache_recursive(child, self.root, 1, idx)
    
    def _build_cache_recursive(
        self,
        element: TreeElement,
        parent: TreeElement | JMeterTestPlan,
        depth: int,
        index: int
    ) -> None:
        self._cache[element.guid] = TreeNodeInfo(
            element=element,
            parent=parent,
            depth=depth,
            index=index
        )
        
        for idx, child in enumerate(element.children):
            self._build_cache_recursive(child, element, depth + 1, idx)
    
    def _get_element_key(self, element: TreeElement | JMeterTestPlan) -> str:
        if isinstance(element, JMeterTestPlan):
            return str(id(element))
        return element.guid
    
    def get_parent(self, element: TreeElement) -> TreeElement | JMeterTestPlan | None:
        self._ensure_cache_valid()
        node_info = self._cache.get(element.guid)
        return node_info.parent if node_info else None
    
    def get_ancestors(self, element: TreeElement) -> list[TreeElement | JMeterTestPlan]:
        self._ensure_cache_valid()
        ancestors = []
        current = element
        
        while True:
            node_info = self._cache.get(current.guid)
            if not node_info or node_info.parent is None:
                break
            ancestors.append(node_info.parent)
            if isinstance(node_info.parent, JMeterTestPlan):
                break
            current = node_info.parent
        
        return ancestors
    
    def get_path(self, element: TreeElement) -> list[TreeElement | JMeterTestPlan]:
        self._ensure_cache_valid()
        ancestors = self.get_ancestors(element)
        ancestors.reverse()
        ancestors.append(element)
        return ancestors
    
    def get_siblings(self, element: TreeElement, include_self: bool = False) -> list[TreeElement]:
        self._ensure_cache_valid()
        parent = self.get_parent(element)
        
        if parent is None:
            return [element] if include_self else []
        
        siblings = [child for child in parent.children]
        
        if not include_self:
            siblings = [s for s in siblings if s.guid != element.guid]
        
        return siblings
    
    def get_index(self, element: TreeElement) -> int:
        self._ensure_cache_valid()
        node_info = self._cache.get(element.guid)
        return node_info.index if node_info else -1
    
    def get_depth(self, element: TreeElement) -> int:
        self._ensure_cache_valid()
        node_info = self._cache.get(element.guid)
        return node_info.depth if node_info else 0
    
    def find_by_guid(self, guid: str) -> TreeElement | None:
        self._ensure_cache_valid()
        node_info = self._cache.get(guid)
        if node_info and isinstance(node_info.element, TreeElement):
            return node_info.element
        return None
    
    def find_by_name(
        self,
        name: str,
        start_from: TreeElement | JMeterTestPlan | None = None
    ) -> TreeElement | None:
        self._ensure_cache_valid()
        start = start_from if start_from else self.root
        
        if isinstance(start, TreeElement) and start.testname == name:
            return start
        
        for child in start.children:
            if child.testname == name:
                return child
            
            result = self.find_by_name(name, child)
            if result:
                return result
        
        return None
    
    def find_all_by_name(self, name: str) -> list[TreeElement]:
        return self.find_all_by_predicate(lambda e: e.testname == name)
    
    def find_by_predicate(
        self,
        predicate: Callable[[TreeElement], bool],
        start_from: TreeElement | JMeterTestPlan | None = None
    ) -> TreeElement | None:
        self._ensure_cache_valid()
        start = start_from if start_from else self.root
        
        if isinstance(start, TreeElement) and predicate(start):
            return start
        
        for child in start.children:
            if predicate(child):
                return child
            
            result = self.find_by_predicate(predicate, child)
            if result:
                return result
        
        return None
    
    def find_all_by_predicate(
        self,
        predicate: Callable[[TreeElement], bool]
    ) -> list[TreeElement]:
        self._ensure_cache_valid()
        results = []
        
        def search_recursive(element: TreeElement | JMeterTestPlan):
            if isinstance(element, TreeElement) and predicate(element):
                results.append(element)
            
            for child in element.children:
                search_recursive(child)
        
        search_recursive(self.root)
        return results
    
    def is_ancestor(
        self,
        ancestor: TreeElement | JMeterTestPlan,
        descendant: TreeElement
    ) -> bool:
        self._ensure_cache_valid()
        ancestors = self.get_ancestors(descendant)
        
        if isinstance(ancestor, JMeterTestPlan):
            return any(isinstance(a, JMeterTestPlan) for a in ancestors)
        
        return any(
            isinstance(a, TreeElement) and a.guid == ancestor.guid
            for a in ancestors
        )
    
    def is_descendant(
        self,
        descendant: TreeElement,
        ancestor: TreeElement | JMeterTestPlan
    ) -> bool:
        return self.is_ancestor(ancestor, descendant)
    
    def is_sibling(self, el1: TreeElement, el2: TreeElement) -> bool:
        self._ensure_cache_valid()
        parent1 = self.get_parent(el1)
        parent2 = self.get_parent(el2)
        
        if parent1 is None or parent2 is None:
            return False
        
        if isinstance(parent1, JMeterTestPlan) and isinstance(parent2, JMeterTestPlan):
            return True
        
        if isinstance(parent1, TreeElement) and isinstance(parent2, TreeElement):
            return parent1.guid == parent2.guid
        
        return False
    
    def is_above(self, el1: TreeElement, el2: TreeElement) -> bool:
        """
        Проверить, находится ли el1 выше el2 в дереве.
        Элемент находится выше, если:
        1. Он является предком el2, или
        2. Они siblings и индекс el1 < индекс el2, или
        3. Их ближайший общий предок имеет потомка-предка el1 с меньшим индексом
        """
        self._ensure_cache_valid()
        
        if self.is_ancestor(el1, el2):
            return True
        
        if self.is_sibling(el1, el2):
            return self.get_index(el1) < self.get_index(el2)
        
        ancestors1 = self.get_path(el1)
        ancestors2 = self.get_path(el2)
        
        common_depth = 0
        for i in range(min(len(ancestors1), len(ancestors2))):
            a1 = ancestors1[i]
            a2 = ancestors2[i]
            
            if isinstance(a1, JMeterTestPlan) or isinstance(a2, JMeterTestPlan):
                if type(a1) == type(a2):
                    common_depth = i + 1
                break
            
            if a1.guid == a2.guid:
                common_depth = i + 1
            else:
                break
        
        if common_depth == 0:
            return False
        
        if common_depth >= len(ancestors1) or common_depth >= len(ancestors2):
            return False
        
        branch1 = ancestors1[common_depth]
        branch2 = ancestors2[common_depth]
        
        if isinstance(branch1, TreeElement) and isinstance(branch2, TreeElement):
            return self.get_index(branch1) < self.get_index(branch2)
        
        return False
    
    def is_below(self, el1: TreeElement, el2: TreeElement) -> bool:
        return self.is_above(el2, el1)
    
    def move(
        self,
        element: TreeElement,
        new_parent: TreeElement | JMeterTestPlan,
        index: int | None = None
    ) -> bool:
        """
        Переместить элемент к новому родителю.
        
        Args:
            element: Элемент для перемещения
            new_parent: Новый родитель
            index: Индекс вставки (None = в конец)
        
        Returns:
            True если перемещение успешно
        
        Note:
            После операции кэш помечается как грязный и будет пересчитан
            автоматически при следующем обращении к методам чтения.
        """
        if not self.validate_move(element, new_parent)[0]:
            return False
        
        old_parent = self.get_parent(element)
        
        if old_parent:
            old_parent.remove_child(element)
        
        new_parent.add_child(element, index)
        
        self._is_dirty = True
        return True
    
    def copy(self, element: TreeElement, deep: bool = True) -> TreeElement:
        """
        Копировать элемент.
        
        Args:
            element: Элемент для копирования
            deep: Копировать с детьми (True) или без (False)
        
        Returns:
            Копия элемента с новым GUID
        """
        import copy as copy_module
        
        if deep:
            copied = copy_module.deepcopy(element)
        else:
            copied = copy_module.copy(element)
            copied.children = []
        
        copied.guid = str(uuid.uuid4())
        
        if deep:
            def regenerate_guids(el: TreeElement):
                el.guid = str(uuid.uuid4())
                for child in el.children:
                    regenerate_guids(child)
            
            for child in copied.children:
                regenerate_guids(child)
        
        return copied
    
    def paste(
        self,
        element: TreeElement,
        target_parent: TreeElement | JMeterTestPlan,
        index: int | None = None
    ) -> TreeElement:
        """
        Вставить копию элемента.
        
        Args:
            element: Элемент для копирования и вставки
            target_parent: Родитель для вставки
            index: Индекс вставки (None = в конец)
        
        Returns:
            Вставленная копия элемента
        
        Note:
            После операции кэш помечается как грязный.
        """
        copied = self.copy(element, deep=True)
        target_parent.add_child(copied, index)
        self._is_dirty = True
        return copied
    
    def delete(self, element: TreeElement) -> bool:
        """
        Удалить элемент из дерева.
        
        Returns:
            True если удаление успешно
        
        Note:
            После операции кэш помечается как грязный.
        """
        parent = self.get_parent(element)
        
        if parent is None:
            return False
        
        parent.remove_child(element)
        self._is_dirty = True
        return True
    
    def swap(self, el1: TreeElement, el2: TreeElement) -> bool:
        """
        Поменять местами два элемента.
        Элементы должны быть siblings (иметь одного родителя).
        
        Returns:
            True если обмен успешен
        
        Note:
            После операции кэш помечается как грязный.
        """
        if not self.is_sibling(el1, el2):
            return False
        
        parent = self.get_parent(el1)
        if parent is None:
            return False
        
        idx1 = self.get_index(el1)
        idx2 = self.get_index(el2)
        
        parent.remove_child(el1)
        parent.remove_child(el2)
        
        if idx1 < idx2:
            parent.add_child(el2, idx1)
            parent.add_child(el1, idx2)
        else:
            parent.add_child(el1, idx2)
            parent.add_child(el2, idx1)
        
        self._is_dirty = True
        return True
    
    def move_batch(
        self,
        elements: list[TreeElement],
        new_parent: TreeElement | JMeterTestPlan,
        start_index: int | None = None
    ) -> int:
        """
        Переместить несколько элементов к новому родителю.
        
        Args:
            elements: Список элементов для перемещения
            new_parent: Новый родитель
            start_index: Начальный индекс вставки (None = в конец)
        
        Returns:
            Количество успешно перемещенных элементов
        
        Note:
            После операции кэш помечается как грязный.
            Рекомендуется явно вызвать rebuild_cache() после завершения.
        """
        moved_count = 0
        current_index = start_index
        
        for element in elements:
            if self.validate_move(element, new_parent)[0]:
                old_parent = self.get_parent(element)
                if old_parent:
                    old_parent.remove_child(element)
                
                new_parent.add_child(element, current_index)
                moved_count += 1
                
                if current_index is not None:
                    current_index += 1
        
        if moved_count > 0:
            self._is_dirty = True
        
        return moved_count
    
    def delete_batch(self, elements: list[TreeElement]) -> int:
        """
        Удалить несколько элементов.
        
        Returns:
            Количество успешно удаленных элементов
        
        Note:
            После операции кэш помечается как грязный.
            Рекомендуется явно вызвать rebuild_cache() после завершения.
        """
        deleted_count = 0
        
        for element in elements:
            parent = self.get_parent(element)
            if parent:
                parent.remove_child(element)
                deleted_count += 1
        
        if deleted_count > 0:
            self._is_dirty = True
        
        return deleted_count
    
    def enable_batch(self, elements: list[TreeElement]) -> int:
        """
        Включить несколько элементов.
        
        Returns:
            Количество включенных элементов
        """
        count = 0
        for element in elements:
            element.enabled = True
            count += 1
        return count
    
    def disable_batch(self, elements: list[TreeElement]) -> int:
        """
        Выключить несколько элементов.
        
        Returns:
            Количество выключенных элементов
        """
        count = 0
        for element in elements:
            element.enabled = False
            count += 1
        return count
    
    def validate_move(
        self,
        element: TreeElement,
        target_parent: TreeElement | JMeterTestPlan
    ) -> tuple[bool, str | None]:
        """
        Проверить возможность перемещения элемента.
        
        Returns:
            (success, error_message)
        """
        if isinstance(target_parent, TreeElement):
            if element.guid == target_parent.guid:
                return (False, "Cannot move element to itself")
            
            if self.is_ancestor(element, target_parent):
                return (False, "Cannot move element to its own descendant")
        
        return (True, None)
    
    def validate_hierarchy(self) -> tuple[bool, list[str]]:
        """
        Проверить целостность дерева.
        
        Returns:
            (is_valid, list_of_errors)
        """
        self._ensure_cache_valid()
        errors = []
        
        visited_guids = set()
        
        def check_recursive(element: TreeElement | JMeterTestPlan, expected_parent):
            if isinstance(element, TreeElement):
                if element.guid in visited_guids:
                    errors.append(f"Duplicate GUID found: {element.guid}")
                    return
                
                visited_guids.add(element.guid)
                
                node_info = self._cache.get(element.guid)
                if not node_info:
                    errors.append(f"Element not in cache: {element.testname}")
                    return
                
                if node_info.parent != expected_parent:
                    errors.append(f"Parent mismatch for: {element.testname}")
            
            for child in element.children:
                check_recursive(child, element)
        
        check_recursive(self.root, None)
        
        return (len(errors) == 0, errors)
    
    def get_statistics(self) -> dict:
        """
        Получить статистику по дереву.
        
        Returns:
            Словарь со статистикой
        """
        self._ensure_cache_valid()
        
        from jmx_builder.models.tree import CategoryElement
        
        stats = {
            "total_elements": 0,
            "max_depth": 0,
            "categories": {},
            "enabled_count": 0,
            "disabled_count": 0
        }
        
        for node_info in self._cache.values():
            element = node_info.element
            
            if isinstance(element, TreeElement):
                stats["total_elements"] += 1
                stats["max_depth"] = max(stats["max_depth"], node_info.depth)
                
                category = element.category.value
                stats["categories"][category] = stats["categories"].get(category, 0) + 1
                
                if element.enabled:
                    stats["enabled_count"] += 1
                else:
                    stats["disabled_count"] += 1
        
        return stats
    
    def visualize_tree(
        self,
        start_from: TreeElement | JMeterTestPlan | None = None
    ) -> str:
        """
        Визуализировать дерево в текстовом формате.
        
        Args:
            start_from: Начать с этого элемента (по умолчанию с root)
        
        Returns:
            Текстовое представление дерева
        """
        from jmx_builder.utility.console import print_tree
        
        start = start_from if start_from else self.root
        return print_tree(start)
    
    def to_xml(self) -> str:
        """
        Получить XML представление дерева.
        
        Returns:
            XML строка
        """
        return self.root.to_xml()