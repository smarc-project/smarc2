"""Pure tests for topic_utils. No ROS running."""

import pytest
from smarc_msgs.msg import Topics

from smarc_utilities.topic_utils import STRING_MSG, StringTopic, string_topics_under

PREFIX = Topics.WARA_PS_SENSOR_PREFIX
FLOAT_MSG = 'std_msgs/msg/Float32'


@pytest.mark.parametrize('root', ['/sam0', '/sam0/', 'sam0'])
def test_topic_under_the_root_and_prefix(root):
    absolute = f'/sam0/{PREFIX}/acoustic'
    found = string_topics_under([(absolute, [STRING_MSG])], root, PREFIX)
    assert found == [StringTopic(absolute=absolute, name='acoustic')]


@pytest.mark.parametrize('root', ['/', ''])
def test_empty_root_means_prefix_at_the_top(root):
    under_agent = f'/sam0/{PREFIX}/acoustic'
    bare = f'/{PREFIX}/acoustic'
    found = string_topics_under([(under_agent, [STRING_MSG]), (bare, [STRING_MSG])], root, PREFIX)
    assert found == [StringTopic(absolute=bare, name='acoustic')]


def test_prefix_later_in_the_name_is_not_under_it():
    # Ozer's #439 case: the prefix has to start right after the root.
    topics = [
        (f'/sam0/otherstuff/{PREFIX}/value', [STRING_MSG]),
        (f'/sam0/{PREFIX}thing/value', [STRING_MSG]),
    ]
    assert string_topics_under(topics, '/sam0', PREFIX) == []


def test_other_roots_are_not_mine():
    topics = [
        (f'/stick_2/{PREFIX}/acoustic', [STRING_MSG]),
        (f'/sam0/{PREFIX}/acoustic', [STRING_MSG]),
    ]
    found = string_topics_under(topics, '/sam0', PREFIX)
    assert [t.absolute for t in found] == [f'/sam0/{PREFIX}/acoustic']


def test_names_may_contain_slashes():
    absolute = f'/sam0/{PREFIX}/acoustic/stick_1/range'
    found = string_topics_under([(absolute, [STRING_MSG])], '/sam0', PREFIX)
    assert found[0].name == 'acoustic/stick_1/range'


def test_the_prefix_itself_is_not_a_sensor():
    assert string_topics_under([(f'/sam0/{PREFIX}', [STRING_MSG])], '/sam0', PREFIX) == []


def test_non_string_types_are_skipped():
    topics = [
        (f'/sam0/{PREFIX}/depth', [FLOAT_MSG]),
        (f'/sam0/{PREFIX}/mixed', [FLOAT_MSG, STRING_MSG]),
    ]
    found = string_topics_under(topics, '/sam0', PREFIX)
    assert [t.name for t in found] == ['mixed']


def test_empty_prefix_finds_nothing():
    topics = [(f'/sam0/{PREFIX}/acoustic', [STRING_MSG])]
    assert string_topics_under(topics, '/sam0', '') == []
    assert string_topics_under(topics, '/sam0', '/') == []


def test_result_is_sorted():
    topics = [
        (f'/sam0/{PREFIX}/speed', [STRING_MSG]),
        (f'/sam0/{PREFIX}/acoustic', [STRING_MSG]),
        (f'/sam0/{PREFIX}/depth', [STRING_MSG]),
    ]
    found = string_topics_under(topics, '/sam0', PREFIX)
    assert [t.name for t in found] == ['acoustic', 'depth', 'speed']
