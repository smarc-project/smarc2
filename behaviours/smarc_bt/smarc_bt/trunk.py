#!/usr/bin/python3

import py_trees as pt
from py_trees.composites import Selector as Fallback
from py_trees.composites import Sequence, Parallel



def make_tree():
    root = Sequence(name="SQ_Root",
                    children=[
                    ])
    tree = pt.trees.BehaviourTree(root)

    return tree


def main():
    tree = make_tree()


if __name__ == "__main__":
    main()