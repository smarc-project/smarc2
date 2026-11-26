"""A running TST: which leaves start, which get cancelled, when it is over. No rclpy.

``start_run`` builds the run from a parsed ``Seq`` or ``Conc`` and names the
leaves that start together. ``next_after_leaf`` is called once a leaf has left
the officer's executing list, and says what follows. The officer does the
sending and cancelling; this module only keeps the tree's state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from waraps_officer.commands import Conc, Leaf, Seq
from waraps_officer.tasks import WaraPSTaskStates


class Phase(Enum):
    IDLE = 'idle'
    LIVE = 'live'
    STOPPING = 'stopping'
    DONE = 'done'
    FAILED = 'failed'


@dataclass
class RunNode:
    """One node of a running TST."""

    tst_node: Leaf | Seq | Conc
    parent: RunNode | None = None
    children: list[RunNode] = field(default_factory=list)
    index: int = 0
    phase: Phase = Phase.IDLE
    fail: str | None = None


@dataclass(frozen=True)
class NextSteps:
    """Leaves to start, task uuids to cancel, and whether the TST is over."""

    start: tuple[Leaf, ...] = ()
    cancel: tuple[str, ...] = ()
    done: bool = False


class MissionRun:
    def __init__(self, root: RunNode) -> None:
        self.root = root
        self.by_uuid: dict[str, RunNode] = {}
        self._index(root)

    def _index(self, node: RunNode) -> None:
        if isinstance(node.tst_node, Leaf):
            self.by_uuid[node.tst_node.task_uuid] = node
        for child in node.children:
            self._index(child)


def start_run(root: Seq | Conc) -> tuple[MissionRun, NextSteps]:
    """The leaves that start now. An empty tree is already done."""
    run = MissionRun(_build_node(root, None))
    start: list[Leaf] = []
    _collect_startable(run.root, start)
    done = not start
    if done:
        run.root.phase = Phase.DONE
    return run, NextSteps(tuple(start), (), done)


def next_after_leaf(run: MissionRun, uuid: str, status: str) -> NextSteps:
    """What to do once a leaf has left the executing list."""
    node = run.by_uuid[uuid]
    node.phase = Phase.DONE if status == WaraPSTaskStates.FINISHED else Phase.FAILED
    start: list[Leaf] = []
    cancel: list[str] = []
    done = _report_to_parent(node.parent, node, status, start, cancel)
    return NextSteps(tuple(start), tuple(cancel), done)


def _build_node(tst_node: Leaf | Seq | Conc, parent: RunNode | None) -> RunNode:
    built = RunNode(tst_node, parent)
    if not isinstance(tst_node, Leaf):
        built.children = [_build_node(child, built) for child in tst_node.children]
    return built


def _collect_startable(node: RunNode, start: list[Leaf]) -> None:
    """Mark the leaves that can start without waiting for a sibling."""
    if node.phase in (Phase.DONE, Phase.FAILED, Phase.STOPPING):
        return
    if isinstance(node.tst_node, Leaf):
        if node.phase is Phase.IDLE:
            node.phase = Phase.LIVE
            start.append(node.tst_node)
        return
    node.phase = Phase.LIVE
    # A seq runs one child at a time; a conc starts all of them.
    if isinstance(node.tst_node, Seq):
        if node.index < len(node.children):
            _collect_startable(node.children[node.index], start)
        return
    for child in node.children:
        _collect_startable(child, start)


def _report_to_parent(
    parent: RunNode | None,
    child: RunNode,
    status: str,
    start: list[Leaf],
    cancel: list[str],
) -> bool:
    """Hand a child's end to its parent. True once the root itself has ended."""
    if parent is None:
        return True
    if isinstance(parent.tst_node, Seq):
        return _seq_child_ended(parent, status, start, cancel)
    return _conc_child_ended(parent, child, status, start, cancel)


def _seq_child_ended(parent: RunNode, status: str, start: list[Leaf], cancel: list[str]) -> bool:
    # A seq already being cancelled from above only waits for its leaves to come back.
    if parent.phase is Phase.STOPPING:
        return _end_when_drained(parent, start, cancel)
    # Any child that did not finish fails the seq: the next step assumed this one worked.
    if status != WaraPSTaskStates.FINISHED:
        parent.phase = Phase.FAILED
        parent.fail = status
        return _report_to_parent(parent.parent, parent, status, start, cancel)
    parent.index += 1
    if parent.index < len(parent.children):
        _collect_startable(parent.children[parent.index], start)
        return False
    parent.phase = Phase.DONE
    return _report_to_parent(parent.parent, parent, WaraPSTaskStates.FINISHED, start, cancel)


def _conc_child_ended(
    parent: RunNode,
    child: RunNode,
    status: str,
    start: list[Leaf],
    cancel: list[str],
) -> bool:
    if parent.phase is Phase.STOPPING:
        return _end_when_drained(parent, start, cancel)
    # stop-on-first ends the conc with its first child; a failed child ends it too.
    if parent.tst_node.stop_on_first or status != WaraPSTaskStates.FINISHED:
        parent.phase = Phase.STOPPING
        if status != WaraPSTaskStates.FINISHED:
            parent.fail = status
        _stop_siblings(parent, cancel, keep=child)
        return _end_when_drained(parent, start, cancel)
    if all(item.phase is Phase.DONE for item in parent.children):
        parent.phase = Phase.DONE
        return _report_to_parent(parent.parent, parent, WaraPSTaskStates.FINISHED, start, cancel)
    return False


def _end_when_drained(parent: RunNode, start: list[Leaf], cancel: list[str]) -> bool:
    """The container is already stopping. It ends when no leaf is still out.

    A cancel is a request, so a cancelled leaf can still be running; the parent
    waits for it instead of reporting done while an action is live.
    """
    if _any_leaf_out(parent):
        return False
    status = parent.fail or WaraPSTaskStates.FINISHED
    parent.phase = Phase.DONE if parent.fail is None else Phase.FAILED
    return _report_to_parent(parent.parent, parent, status, start, cancel)


def _stop_siblings(parent: RunNode, cancel: list[str], keep: RunNode) -> None:
    for child in parent.children:
        if child is keep:
            continue
        _stop_subtree(child, cancel)


def _stop_subtree(node: RunNode, cancel: list[str]) -> None:
    if isinstance(node.tst_node, Leaf):
        # A live leaf needs a cancel sent; one that never started is simply done.
        if node.phase is Phase.LIVE:
            node.phase = Phase.STOPPING
            cancel.append(node.tst_node.task_uuid)
        elif node.phase is Phase.IDLE:
            node.phase = Phase.DONE
        return
    if node.phase not in (Phase.DONE, Phase.FAILED):
        node.phase = Phase.STOPPING
    for child in node.children:
        _stop_subtree(child, cancel)


def _any_leaf_out(node: RunNode) -> bool:
    if isinstance(node.tst_node, Leaf):
        return node.phase in (Phase.LIVE, Phase.STOPPING)
    return any(_any_leaf_out(child) for child in node.children)
