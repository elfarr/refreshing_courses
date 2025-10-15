from dataclasses import dataclass


# после создания нельзя менять поля. датакласс сразу сам сделает инит
@dataclass(frozen=True)
class QuerySpec:
    where: str = ""
    params: tuple = ()
    order_by: str = ""
