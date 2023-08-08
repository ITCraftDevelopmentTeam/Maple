import json
from pathlib import Path
from typing import Any, Callable, TypeVar, Generic


KT = TypeVar("KT")
VT = TypeVar("VT")


def load_json(path: Path, default_factory: Callable[[], VT] = dict) -> VT:
    if not path.exists():
        data = default_factory()
        dump_json(data, path)
        return data
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def dump_json(obj: Any, path: Path) -> None:
    if not (parent := path.parent).exists():
        parent.mkdir()
    with open(path, "w", encoding="utf-8") as file:
        json.dump(obj, file, ensure_ascii=False, indent=2, sort_keys=True)


class JsonDict(dict, Generic[KT, VT]):
    def __init__(
        self,
        path: Path,
        default_factory: Callable[[], VT] = int
    ) -> None:
        self.path = Path("data", path)
        super().__init__(load_json(self.path))
        self.default_factory = default_factory

    def __missing__(self, __key: KT) -> VT:
        return self.default_factory()

    def __setitem__(self, __key: Any, __value: Any) -> None:
        super().__setitem__(__key, __value)
        self.save()

    def update(self, *args: Any, **kwargs: VT) -> None:
        super().update(*args, **kwargs)
        self.save()

    def save(self) -> None:
        dump_json(self, self.path)
