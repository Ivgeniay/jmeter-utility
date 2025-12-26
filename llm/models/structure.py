from dataclasses import dataclass, field


@dataclass
class EntryInfo:
    index: int
    method: str
    path: str
    status_code: int


@dataclass
class TransactionDefinition:
    name: str
    start_index: int
    end_index: int
    description: str = ""
    
    @property
    def entry_count(self) -> int:
        return self.end_index - self.start_index + 1


@dataclass
class StructureInput:
    entries: list[EntryInfo]
    scenario_number: int = 1
    user_hints: str | None = None


@dataclass
class StructureOutput:
    transactions: list[TransactionDefinition]
    
    def get_covered_indices(self) -> set[int]:
        covered = set()
        for tx in self.transactions:
            for i in range(tx.start_index, tx.end_index + 1):
                covered.add(i)
        return covered
    
    def get_uncovered_indices(self, total_entries: int) -> set[int]:
        covered = self.get_covered_indices()
        all_indices = set(range(total_entries))
        return all_indices - covered
    
    def has_overlaps(self) -> list[tuple[str, str, list[int]]]:
        overlaps = []
        for i, tx1 in enumerate(self.transactions):
            for tx2 in self.transactions[i + 1:]:
                range1 = set(range(tx1.start_index, tx1.end_index + 1))
                range2 = set(range(tx2.start_index, tx2.end_index + 1))
                overlap = range1 & range2
                if overlap:
                    overlaps.append((tx1.name, tx2.name, sorted(overlap)))
        return overlaps
    
    def to_json(self) -> list[dict]:
        return [
            {
                "name": tx.name,
                "start_index": tx.start_index,
                "end_index": tx.end_index,
                "description": tx.description,
            }
            for tx in self.transactions
        ]