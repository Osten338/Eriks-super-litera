from app.services.compare_engine import run_compare


def test_simple_insert_delete():
    orig = [{"text": "Hello world."}]
    mod = [{"text": "Hello brave world!"}]
    res = run_compare(orig, mod, {"includeFormatting": True})
    assert res.stats.total >= 1
    assert len(res.paragraphs) == 1
    html = res.paragraphs[0].html
    assert "diff-insert" in html or "diff-delete" in html


