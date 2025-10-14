from dataclasses import dataclass
from typing import Callable, Any
from Instructor import Instructor

@dataclass(frozen=True)
class FileQuerySpec:
    # фильтр функция 
    predicate: Callable[[Instructor], bool] | None = None 
    # ключ сортироки
    key: Callable[[Instructor], Any] | None = None 
    # перевернутость       
    reverse: bool = False                                    
