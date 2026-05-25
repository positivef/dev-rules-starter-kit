from workflow_dashboard.render import render_html


def _model():
    return {
        "generated_at": "2026-05-24T16:00:00+00:00",
        "config": {"freshness_minutes": 30, "stale_days": 3, "recent_days": 7},
        "projects": [
            {
                "name": "fieldsync-pro",
                "path": "C:/proj",
                "git": {
                    "branch": "main",
                    "uncommitted": 4,
                    "unpushed": 0,
                    "commits_24h": 2,
                    "worktrees": ["main"],
                },
                "slots": [
                    {
                        "slot": "claude-1",
                        "topic": "벤더 P1",
                        "status": "in-progress",
                        "last_updated": "2026-05-24T15:00:00+00:00",
                        "note": None,
                    }
                ],
                "sessions": [
                    {
                        "id_short": "aaaaaaaa",
                        "title": "dev",
                        "branch": "main",
                        "last_activity": "2026-05-24T15:58:00.000Z",
                        "live": True,
                        "pr": 13,
                    }
                ],
                "conflicts": [
                    {
                        "rule": "uncommitted_drift",
                        "severity": "yellow",
                        "detail": "4 uncommitted, 0 unpushed",
                    }
                ],
            }
        ],
    }


def test_render_html_is_self_contained():
    html = render_html(_model())
    assert html.lstrip().startswith("<!DOCTYPE html>")
    assert "const MODEL" in html
    assert "fieldsync-pro" in html
    # Korean topic preserved (UTF-8, not escaped to ascii)
    assert "벤더 P1" in html
    # no external network deps
    assert "http://" not in html and "https://" not in html


def test_render_html_escapes_script_close_in_data():
    model = _model()
    model["projects"][0]["slots"][0]["topic"] = "danger </script><script>x"
    html = render_html(model)
    # the literal closing tag from data must not appear unescaped
    assert "</script><script>x" not in html
    assert "<\\/script>" in html
