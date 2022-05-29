from typing import List

from treelib import Tree

from ModelTuning.Features.MCFeatureNode import MCFeatureNode


class MCFeatureTree:

    def __init__(self):
        self.__tree = Tree()
        root_node = MCFeatureNode(
            identifier="root",
            max_score=0,
            n_visits=0,
            state=[],
        )
        self.add_root(root_node)

    def add_root(self, root_node: MCFeatureNode):
        node_data = {"node": root_node}
        self.__tree.create_node(identifier=root_node.identifier, data=node_data)

    def add_node(self, node: MCFeatureNode, parent: MCFeatureNode) -> MCFeatureNode:
        node_data = {"node": node}
        self.__tree.create_node(identifier=node.identifier, data=node_data, parent=self.to_treelib_node(parent))
        return node

    def node(self, identifier: str) -> MCFeatureNode:
        return self.__tree.get_node(identifier).data["node"]

    def parent(self, identifier: str) -> MCFeatureNode:
        return self.__tree.parent(identifier).data["node"]

    def children(self, identifier: str) -> List[MCFeatureNode]:
        treelib_children = self.__tree.children(identifier)
        return [treelib_child.data["node"] for treelib_child in treelib_children]

    def to_treelib_node(self, node: MCFeatureNode):
        return self.__tree.get_node(node.identifier)
