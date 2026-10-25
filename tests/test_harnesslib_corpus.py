from pathlib import Path

from harnesslib import corpus
import utils


def test_utils_reexports_are_the_same_objects():
    for name in ("NAME_MAX_BYTES", "_truncate_with_hash", "project_key", "project_prefix",
                 "filter_manifest_by_repo"):
        assert getattr(utils, name) is getattr(corpus, name)


def test_corpus_takes_repos_dir_explicitly(tmp_path):
    p = tmp_path / "R" / "o" / "r" / "sub" / "b.kicad_pcb"
    assert corpus.repo_name_from_path(p, tmp_path / "R") == "o/r"
    assert corpus.within_repo_path(p, tmp_path / "R") == "sub/b.kicad_pcb"
    assert corpus.safe_name(p, tmp_path / "R") == "sub_b.kicad_pcb"


def test_harnesslib_corpus_imports_no_harness_layers():
    src = (Path(corpus.__file__)).read_text()
    for banned in ("import utils", "from utils", "regression", "from run", "import run"):
        assert banned not in src
