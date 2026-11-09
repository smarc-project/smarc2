"""Find the std_msgs/String topics that live under a prefix.

Used by anything that forwards or advertises a family of String topics
without listing them one by one: the WARA-PS bridge forwards everything
under ``Topics.WARA_PS_SENSOR_PREFIX``, and the WARA-PS vehicle node lists
the same set in ``sensor_info``.

``string_topics_under`` is pure and takes the graph as data, so it is tested
without ROS. ``node_string_topics_under`` reads the graph from a live node
and drops topics nobody actually publishes.
"""

from dataclasses import dataclass

STRING_MSG = 'std_msgs/msg/String'


@dataclass(frozen=True)
class StringTopic:
    """One String topic found under the prefix.

    ``absolute`` is the full graph name; subscribe with it. ``name`` is what
    follows the prefix, slashes included.
    """
    absolute: str
    name: str


def _segments(path):
    return [s for s in path.split('/') if s]


def string_topics_under(topics, root, prefix):
    """String topics named ``<root>/<prefix>/<name>``.

    ``topics`` is what ``Node.get_topic_names_and_types`` returns. ``root`` is
    the namespace the prefix hangs off, normally the robot's. ``prefix`` is a
    Topics constant such as ``Topics.WARA_PS_SENSOR_PREFIX``.

    The prefix has to start right after the root. A topic with the prefix
    somewhere later in its name is not under it. Returns a list sorted by
    absolute name.
    """
    head = _segments(root) + _segments(prefix)
    if not _segments(prefix):
        return []

    found = []
    for absolute, types in topics:
        if STRING_MSG not in types:
            continue
        segments = _segments(absolute)
        if segments[:len(head)] != head:
            continue
        name_segments = segments[len(head):]
        if not name_segments:
            continue
        found.append(StringTopic(absolute=absolute, name='/'.join(name_segments)))
    found.sort(key=lambda t: t.absolute)
    return found


def _published_as_string(node, absolute, include_own):
    for info in node.get_publishers_info_by_topic(absolute):
        if info.topic_type != STRING_MSG:
            continue
        if not include_own and info.node_name == node.get_name() and info.node_namespace == node.get_namespace():
            continue
        return True
    return False


def node_string_topics_under(node, root, prefix, include_own):
    """``string_topics_under`` on a live node's graph, keeping only topics
    some node publishes as a String.

    A topic that is in the graph only because of a subscriber is dropped.
    With ``include_own=False`` the node's own publishers do not count: a
    bridge that mirrors MQTT agents into ROS must not pick its own mirrors
    back up and forward them out again. A vehicle node that advertises what
    it publishes wants ``include_own=True``.
    """
    found = string_topics_under(node.get_topic_names_and_types(), root, prefix)
    return [t for t in found if _published_as_string(node, t.absolute, include_own)]
