from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from models import JMeterResult, Request
from console import Log, NullLog


@dataclass
class MatchedPair:
    har_request: Request
    jmeter_request: Request
    har_index: int
    jmeter_index: int


@dataclass
class UnmatchedRequest:
    request: Request
    index: int
    source: str


@dataclass
class CompareResult:
    log: Log | None = None
    matched: list[MatchedPair] = field(default_factory=list)
    only_in_har: list[UnmatchedRequest] = field(default_factory=list)
    only_in_jmeter: list[UnmatchedRequest] = field(default_factory=list)

    def __post_init__(self):
        if self.log is None:
            self.log = NullLog()
    
    def print_summary(self):
        self.log.log(f'Matched: {len(self.matched)}')
        self.log.log(f'Only in HAR: {len(self.only_in_har)}')
        self.log.log(f'Only in JMeter: {len(self.only_in_jmeter)}')
    
    def print_details(self):
        if self.only_in_har:
            self.log.log('\n--- Only in HAR (missing in JMeter) ---')
            for item in self.only_in_har:
                self.log.log(f'  [{item.index}] {item.request.method} {item.request.url}')
        
        if self.only_in_jmeter:
            self.log.log('\n--- Only in JMeter (not in HAR) ---')
            for item in self.only_in_jmeter:
                self.log.log(f'  [{item.index}] {item.request.method} {item.request.url}')


@dataclass
class TransactionCompareResult:
    log: Log | None = None
    transaction_results: dict[str, CompareResult] = field(default_factory=dict)
    total_matched: int = 0
    total_only_in_har: int = 0
    total_only_in_jmeter: int = 0

    def __post_init__(self):
        if self.log is None:
            self.log = NullLog()
    
    def print_summary(self):
        self.log.log(f'\n=== Overall Summary ===')
        self.log.log(f'Total matched: {self.total_matched}')
        self.log.log(f'Total only in HAR: {self.total_only_in_har}')
        self.log.log(f'Total only in JMeter: {self.total_only_in_jmeter}')
        self.log.log(f'Transactions analyzed: {len(self.transaction_results)}')
    
    def print_details(self):
        for tx_name, result in self.transaction_results.items():
            self.log.log(f'\n=== Transaction: {tx_name} ===')
            result.print_summary()
            result.print_details()


class BaseComparer(ABC):
    def __init__(self, log: Log | None):
        self.log = log

    @abstractmethod
    def compare(self, har_requests: list[Request], jmeter_requests: list[Request]) -> CompareResult:
        pass
    
    @abstractmethod
    def get_key(self, request: Request) -> str:
        pass


class SimpleComparer(BaseComparer):
    def __init__(self, log: Log | None):
        super().__init__(log)

    def compare(self, har_requests: list[Request], jmeter_requests: list[Request]) -> CompareResult:
        result = CompareResult()
        result.log = self.log
        
        jmeter_used = [False] * len(jmeter_requests)
        
        for har_idx, har_req in enumerate(har_requests):
            har_key = self.get_key(har_req)
            found = False
            
            for jmeter_idx, jmeter_req in enumerate(jmeter_requests):
                if jmeter_used[jmeter_idx]:
                    continue
                
                jmeter_key = self.get_key(jmeter_req)
                
                if har_key == jmeter_key:
                    result.matched.append(MatchedPair(
                        har_request=har_req,
                        jmeter_request=jmeter_req,
                        har_index=har_idx,
                        jmeter_index=jmeter_idx
                    ))
                    jmeter_used[jmeter_idx] = True
                    found = True
                    break
            
            if not found:
                result.only_in_har.append(UnmatchedRequest(
                    request=har_req,
                    index=har_idx,
                    source='har'
                ))
        
        for jmeter_idx, used in enumerate(jmeter_used):
            if not used:
                result.only_in_jmeter.append(UnmatchedRequest(
                    request=jmeter_requests[jmeter_idx],
                    index=jmeter_idx,
                    source='jmeter'
                ))
        
        return result
    
    def get_key(self, request: Request) -> str:
        return f'{request.method} {request.url}'
    

class TransactionComparer:
    def __init__(self, base_comparer: BaseComparer, log: Log | None = None):
        self.base_comparer = base_comparer
        self.log = log if log else NullLog()
    
    def compare(self, har_requests: list[Request], jmeter_result: JMeterResult) -> TransactionCompareResult:
        result = TransactionCompareResult(log=self.log)
        
        if not jmeter_result.transactions:
            self.log.log('No transactions found, falling back to simple comparison')
            simple_result = self.base_comparer.compare(har_requests, jmeter_result.all_requests)
            result.transaction_results['__all__'] = simple_result
            result.total_matched = len(simple_result.matched)
            result.total_only_in_har = len(simple_result.only_in_har)
            result.total_only_in_jmeter = len(simple_result.only_in_jmeter)
            return result
        
        har_index = 0
        
        for transaction in jmeter_result.transactions:
            if not transaction.requests:
                self.log.log(f'Skipping empty transaction: {transaction.name}')
                continue
            
            first_request = transaction.requests[0]
            first_key = self.base_comparer.get_key(first_request)
            self.log.log(f'Looking for transaction "{transaction.name}" start: {first_key}')
            
            tx_start_in_har = None
            for i in range(har_index, len(har_requests)):
                if self.base_comparer.get_key(har_requests[i]) == first_key:
                    tx_start_in_har = i
                    break
            
            if tx_start_in_har is None:
                self.log.log(f'Warning: Could not find start of transaction "{transaction.name}" in HAR')
                continue
            
            har_index = tx_start_in_har
        
        har_index = 0
        
        for tx_idx, transaction in enumerate(jmeter_result.transactions):
            if not transaction.requests:
                continue
            
            first_request = transaction.requests[0]
            first_key = self.base_comparer.get_key(first_request)
            
            tx_start_in_har = None
            for i in range(har_index, len(har_requests)):
                if self.base_comparer.get_key(har_requests[i]) == first_key:
                    tx_start_in_har = i
                    break
            
            if tx_start_in_har is None:
                continue
            
            tx_end_in_har = len(har_requests)
            if tx_idx + 1 < len(jmeter_result.transactions):
                next_tx = jmeter_result.transactions[tx_idx + 1]
                if next_tx.requests:
                    next_first_key = self.base_comparer.get_key(next_tx.requests[0])
                    for i in range(tx_start_in_har + 1, len(har_requests)):
                        if self.base_comparer.get_key(har_requests[i]) == next_first_key:
                            tx_end_in_har = i
                            break
            
            har_slice = har_requests[tx_start_in_har:tx_end_in_har]
            
            self.log.log(f'Comparing transaction "{transaction.name}": HAR[{tx_start_in_har}:{tx_end_in_har}] ({len(har_slice)} requests) vs JMeter ({len(transaction.requests)} requests)')
            
            tx_result = self.base_comparer.compare(har_slice, transaction.requests)
            tx_result.log = self.log
            
            for item in tx_result.only_in_har:
                item.transaction_name = transaction.name
                item.index = tx_start_in_har + item.index
            
            for item in tx_result.only_in_jmeter:
                item.transaction_name = transaction.name
            
            result.transaction_results[transaction.name] = tx_result
            result.total_matched += len(tx_result.matched)
            result.total_only_in_har += len(tx_result.only_in_har)
            result.total_only_in_jmeter += len(tx_result.only_in_jmeter)
            
            har_index = tx_end_in_har
        
        return result