from pathlib import Path

from workflow_dashboard.gitinfo import collect_git_info, GitInfo


def make_runner(responses):
    """responses: dict mapping the git subcommand (args[0]) to stdout str."""

    def runner(args, cwd):
        return responses.get(args[0], "")

    return runner


def test_collect_git_info_parses_all_fields():
    responses = {
        "rev-parse": "worktree-vendors-p1-fix",
        "status": " M a.py\n?? b.py\n",
        "rev-list": "2",
        "log": "aaa commit1\nbbb commit2\nccc commit3\n",
        "worktree": (
            "worktree C:/proj\nHEAD 111\nbranch refs/heads/main\n\n"
            "worktree C:/proj/.claude/worktrees/x\nHEAD 222\n"
            "branch refs/heads/feature\n"
        ),
    }
    gi = collect_git_info(Path("C:/proj"), runner=make_runner(responses), window_hours=24)
    assert gi.branch == "worktree-vendors-p1-fix"
    assert gi.uncommitted == 2
    assert gi.unpushed == 2
    assert gi.commits_24h == 3
    assert gi.worktrees == ["main", "feature"]


def test_collect_git_info_failsafe_on_runner_error():
    def boom(args, cwd):
        raise RuntimeError("git not found")

    gi = collect_git_info(Path("C:/proj"), runner=boom)
    assert gi == GitInfo(branch=None, uncommitted=0, unpushed=0, commits_24h=0, worktrees=[])


def test_collect_git_info_no_upstream():
    responses = {
        "rev-parse": "main",
        "status": "",
        "log": "",
        "worktree": "worktree C:/proj\nbranch refs/heads/main\n",
    }
    # rev-list returns "" (no upstream) -> unpushed stays 0
    gi = collect_git_info(Path("C:/proj"), runner=make_runner(responses))
    assert gi.unpushed == 0
    assert gi.uncommitted == 0
    assert gi.commits_24h == 0
