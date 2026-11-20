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


def _under(namespace, root):
    return _segments(namespace)[:len(_segments(root))] == _segments(root)


def _published_as_string_under(node, absolute, root):
    return any(info.topic_type == STRING_MSG and _under(info.node_namespace, root)
               for info in node.get_publishers_info_by_topic(absolute))


def node_string_topics_under(node, root, prefix):
    """``string_topics_under`` on a live node's graph, keeping only topics
    that a node living under ``root`` publishes as a String.

    A topic that is in the graph only because of a subscriber is dropped. So
    is one that only a node from another namespace publishes: a robot's
    sensors come from the robot's own nodes. In simulation several robots
    share one graph, and another robot's bridge publishes its mirrors of our
    sensors from its own namespace; those are not ours to advertise or
    forward.
    """
    found = string_topics_under(node.get_topic_names_and_types(), root, prefix)
    return [t for t in found if _published_as_string_under(node, t.absolute, root)]
