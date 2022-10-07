from typing import List

import numpy as np
from treelib import Tree

from ModelTuning.RankerConfigMCTS.BetModelConfigurationNode import BetModelConfigurationNode
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration


class BetModelConfigurationTree:

    def __init__(self, root_node: BetModelConfigurationNode):
        self.__tree = Tree()
        self.add_root(root_node)

    def add_root(self, root_node: BetModelConfigurationNode):
        node_data = {"node": root_node}
        self.__tree.create_node(identifier=root_node.identifier, data=node_data)

    def add_node(self, node: BetModelConfigurationNode, parent: BetModelConfigurationNode) -> BetModelConfigurationNode:
        node_data = {"node": node}
        self.__tree.create_node(identifier=node.identifier, data=node_data, parent=self.to_treelib_node(parent))
        return node

    def node(self, identifier: str) -> BetModelConfigurationNode:
        return self.__tree.get_node(identifier).data["node"]

    def parent(self, identifier: str) -> BetModelConfigurationNode:
        return self.__tree.parent(identifier).data["node"]

    def children(self, identifier: str) -> List[BetModelConfigurationNode]:
        treelib_children = self.__tree.children(identifier)
        return [treelib_child.data["node"] for treelib_child in treelib_children]

    def to_treelib_node(self, node: BetModelConfigurationNode):
        return self.__tree.get_node(node.identifier)
