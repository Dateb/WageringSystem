from typing import List

from treelib import Tree

from ModelTuning.RankerConfigMCTS.RankerConfigNode import RankerConfigNode
from ModelTuning.RankerConfigMCTS.RankerConfig import RankerConfig


class RankerConfigurationTree:

    def __init__(self):
        self.__tree = Tree()
        root_node = RankerConfigNode(
            identifier="root",
            max_score=0,
            n_visits=0,
            ranker_config=RankerConfig([]),
        )
        self.add_root(root_node)

    def add_root(self, root_node: RankerConfigNode):
        node_data = {"node": root_node}
        self.__tree.create_node(identifier=root_node.identifier, data=node_data)

    def add_node(self, node: RankerConfigNode, parent: RankerConfigNode) -> RankerConfigNode:
        node_data = {"node": node}
        self.__tree.create_node(identifier=node.identifier, data=node_data, parent=self.to_treelib_node(parent))
        return node

    def node(self, identifier: str) -> RankerConfigNode:
        return self.__tree.get_node(identifier).data["node"]

    def parent(self, identifier: str) -> RankerConfigNode:
        return self.__tree.parent(identifier).data["node"]

    def children(self, identifier: str) -> List[RankerConfigNode]:
        treelib_children = self.__tree.children(identifier)
        return [treelib_child.data["node"] for treelib_child in treelib_children]

    def to_treelib_node(self, node: RankerConfigNode):
        return self.__tree.get_node(node.identifier)
