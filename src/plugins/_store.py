import json
from pathlib import Path
from typing import cast, Any, Generic, TypeVar, Callable, Optional

from ._sorcery import modulename


BASE_PATH = Path('data')
_VT = TypeVar('_VT')


def _load(path: Path, default: Any = None) -> Any:
    if not path.exists():
        _dump(default, path)
        return default
    with open(path, 'r') as file:
        return json.load(file)


def _dump(obj: Any, path: Path) -> None:
    if not (parent := path.parent).exists():
        parent.mkdir()
    with open(path, 'w') as file:
        json.dump(obj, file, ensure_ascii=False, indent=2, sort_keys=True)


class Json(Generic[_VT]):
    def __init__(
        self,
        filepath: Path | str,
        schema: type[_VT],
        /, *args: Any,
        default: Optional[Callable[[], _VT] | _VT] = None,
        **kwargs: Any,
    ) -> None:
        filepath = Path(filepath)
        stem = filepath.stem
        if stem.startswith('.'):
            stem = modulename(depth=1) + stem
        if not stem.endswith('.json'):
            stem = stem + '.json'
        self.path = BASE_PATH / filepath.parent / stem
        self.schema = schema
        self.factory = cast(Callable[[], _VT], (
            default if callable(default)
            else lambda: cast(_VT, default)
        ) if default is not None else schema)
        self.args, self.kwargs = args, kwargs

    def __enter__(self) -> _VT:
        self.data = self._
        return self.data

    def __exit__(self, *exc: Any) -> None:
        _dump(self.data, self.path)

    @property
    def _(self):
        return self.schema(
            _load(self.path, self.factory()),
            *self.args, **self.kwargs
        )
