import os
import json
from typing import Any, Callable, TypeVar, Generic


T = TypeVar("T")


def load_json(path: str, default_factory: Callable[[], T] = dict) -> T:
    if not os.path.exists(path):
        return default_factory()
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def dump_json(obj: Any, path: str) -> None:
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as file:
        json.dump(obj, file, ensure_ascii=False, indent=2, sort_keys=True)


class JsonDict(dict, Generic[T]):
    def __init__(
        self,
        path: str,
        default_factory: Callable[[], T] = int
    ) -> None:
        self.path = os.path.join("data", path)
        data = load_json(self.path)
        assert isinstance(data, dict)
        super().__init__(data)
        self.default_factory = default_factory

    def __getitem__(self, __key: Any) -> T:
        if __key not in self.keys():
            super().__setitem__(__key, self.default_factory())
        self.save()
        return super().__getitem__(__key)

    def __setitem__(self, __key: Any, __value: Any) -> None:
        super().__setitem__(__key, __value)
        self.save()

    def __delitem__(self, __key: Any) -> None:
        super().__delitem__(__key)
        self.save()

    def save(self) -> None:
        dump_json(self, self.path)

    def __del__(self) -> None:
        self.save()
