# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from functools import cached_property
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import pandas as pd

from opsml.registry.cards import ArtifactCard, PipelineCard
from opsml.registry.cards.types import (
    NON_PIPELINE_CARDS,
    CardType,
    PipelineCardArgs,
    RunCardArgs,
)
from opsml.registry.sql.registry import CardRegistry

DATA_ATTRS = ["name", "team", "version", "data_type", "dependent_vars"]
MODEL_ATTRS = ["name", "team", "version", "datacard_uid", "model_type"]
EXP_ATTRS = [PipelineCardArgs.DATA_UIDS, PipelineCardArgs.MODEL_UIDS, "metrics"]
POP_ATTRS = [PipelineCardArgs.DATA_UIDS, PipelineCardArgs.MODEL_UIDS, "datacard_uid"]


class Visualizer:
    def __init__(
        self,
        relationships: Dict[str, List[Optional[str]]],
        pipeline_card_name: str,
    ):
        """Creates a visualize class to build a graphviz object

        Args:
            relationships (Dict): Dictionary of artifact relationships
            pipeline_card_name (str): Name of pipeline
        """
        self.relationships = relationships
        self.pipeline_name = pipeline_card_name
        self.main_node_style = {
            "style": "rounded, filled",
            "fontname": "arial",
            "shape": "rect",
            "fillcolor": "#a7ebc4",
        }

        self.attr_node_style = {
            "style": "filled",
            "fontname": "arial",
            "fontsize": "10",
            "shape": "folder",
            "fillcolor": "#Dcd3e6",
        }

    def _get_name_val(self, lines: List[Optional[str]], attributes: Dict[str, Any]) -> List[Optional[str]]:
        for name, value in attributes.items():
            if isinstance(value, dict):
                return self._get_name_val(lines, value)
            lines.append(f"{name}={value}")
        return lines

    def _parse_attrs(self, attributes: Dict[str, Any]) -> Optional[str]:
        for pop_attr in POP_ATTRS:
            attributes.pop(pop_attr, None)

        if bool(attributes):
            lines: List[Optional[str]] = []
            self._get_name_val(lines=lines, attributes=attributes)
            return "\n".join(cast(List[str], lines))
        return None

    def _create_attr_node(self, name: str, attributes: Dict[str, Any], graph: Any):
        attrs = self._parse_attrs(attributes=attributes)
        if bool(attrs):
            graph.node(f"{name}_attr", label=attrs, **self.attr_node_style)
            graph.edge(name, f"{name}_attr", arrowhead="none")

    def _create_main_nodes(self, graph: Any) -> None:
        for name in self.relationships:
            graph.node(name, **self.main_node_style)

    def _create_attr_depen_nodes(self, graph=Any) -> None:
        for name, meta in self.relationships.items():
            meta_dict = cast(Dict[str, Union[Dict[str, Any], List[str]]], meta)

            if meta_dict.get("attributes") is not None:
                attributes = cast(Dict[str, Any], meta_dict.get("attributes"))
                self._create_attr_node(name=name, attributes=attributes, graph=graph)

            if meta_dict.get("dependencies") is not None:
                dependencies = cast(List[str], meta_dict.get("dependencies"))
                for dependency in dependencies:
                    graph.edge(dependency, name)

    def graph(self):
        """Creates pipeline graph from pipeline artifact card relationships"""
        from graphviz import Digraph  # pylint: disable=import-outside-toplevel

        graph = Digraph(name=self.pipeline_name, format="png")
        graph.attr(
            "graph",
            label=self.pipeline_name.replace("_", " "),
            fontname="arial",
            title="",
            rankdir="LR",
        )

        self._create_main_nodes(graph=graph)
        self._create_attr_depen_nodes(graph=graph)

        return graph


class DependencyParser:
    def __init__(
        self,
        registries: Dict[str, CardRegistry],
        card_uids: Dict[str, Dict[str, str]],
    ):
        self.registries = registries
        self.card_uids = card_uids
        self.card_dependencies: Dict[str, Any] = {}

    def _get_card_attr(self, card_metadata: Dict[str, str]) -> Tuple[str, str]:
        card_type = str(card_metadata.get("card_type"))
        uid = str(card_metadata.get("uid"))
        return card_type, uid

    def _get_artifact_attr(
        self, card_uid: str, registry_type: str, attributes: List[str]
    ) -> Dict[str, Union[str, int, float]]:
        registry = self.registries[registry_type]
        cards: pd.DataFrame = registry.list_cards(uid=card_uid)
        attr = cards[attributes][0:1].T.to_dict()[0]
        return attr

    def _get_artifact_names(self, card_record: Dict[str, Any], key_name: str, card_type: str) -> List[str]:
        artifact_names = []
        for uid in cast(List[str], card_record.get(key_name)):
            data_name = self._get_artifact_attr(
                card_uid=uid,
                registry_type=card_type,
                attributes=["name"],
            )
            artifact_names.append(str(data_name["name"]))
        return artifact_names

    def _parse_card(self, card: str, card_type: str, card_uid: str):
        if card_type == "data":
            card_attr = self._get_artifact_attr(card_uid=card_uid, registry_type=card_type, attributes=DATA_ATTRS)
            self.card_dependencies[card] = {
                "dependencies": [],
                "attributes": card_attr,
            }

        elif card_type == "model":
            card_attr = self._get_artifact_attr(card_uid=card_uid, registry_type=card_type, attributes=MODEL_ATTRS)
            datacard_uid = str(card_attr.get(RunCardArgs.DATA_UID))
            data_attr = self._get_artifact_attr(
                card_uid=datacard_uid,
                registry_type="data",
                attributes=["name"],
            )
            self.card_dependencies[card] = {"dependencies": [data_attr["name"]], "attributes": card_attr}

        else:
            artifact_names = []
            card_attr = self._get_artifact_attr(card_uid=card_uid, registry_type=card_type, attributes=EXP_ATTRS)
            for key_name, type_ in zip(
                [PipelineCardArgs.DATA_UIDS, PipelineCardArgs.MODEL_UIDS],
                ["data", "model"],
            ):
                if bool(card_attr.get(key_name)):
                    artifact_names.extend(
                        self._get_artifact_names(
                            card_record=card_attr,
                            key_name=key_name,
                            card_type=type_,
                        )
                    )
            self.card_dependencies[card] = {"dependencies": artifact_names, "attributes": card_attr}

    def get_relationships(self):
        for card, metadata in self.card_uids.items():
            card_type, card_uid = self._get_card_attr(card_metadata=metadata)
            self._parse_card(card=card, card_type=card_type, card_uid=card_uid)


class PipelineLoader:
    def __init__(self, pipelinecard_uid: str):
        """Loads all cards assoicated with a PipelineCard.

        Args:
            pipelinecard_uid (str) Uid of a PipelineCard
        """
        self.pipline_card = self._load_pipeline_card(uid=pipelinecard_uid)
        self._card_deck: Dict[str, List[ArtifactCard]] = {}

    def _load_pipeline_card(self, uid: str) -> PipelineCard:
        registry = CardRegistry(registry_name=CardType.PIPELINECARD.value)
        loaded_card = registry.load_card(uid=uid)
        return cast(PipelineCard, loaded_card)

    def _load_cards(self, cards: Dict[str, str], card_type: str):
        card_list = [self._registries[card_type].load_card(uid=card_uid) for card_uid in cards]

        self._card_deck[card_type] = card_list

    def load_cards(self):
        for card_type in NON_PIPELINE_CARDS:
            cards = getattr(self.pipline_card, f"{card_type}card_uids")
            if bool(cards):
                self._load_cards(cards=cards, card_type=card_type)

        return self._card_deck

    @cached_property
    def card_uids(self) -> Dict[str, Dict[str, str]]:
        card_uids = cast(Dict[str, Dict[str, str]], {})

        for card_type in NON_PIPELINE_CARDS:
            cards = getattr(self.pipline_card, f"{card_type}card_uids")
            if bool(cards):
                card_uids[card_type] = cards

        return card_uids

    @cached_property
    def _registries(self):
        registries = {}
        for name in ["data", "model", "run"]:
            registries[name] = CardRegistry(name)
        return registries

    def _get_relationships(self):
        depen_parser = DependencyParser(
            registries=self._registries,
            card_uids=self.card_uids,
        )
        depen_parser.get_relationships()

        viz = Visualizer(
            relationships=depen_parser.card_dependencies,
            pipeline_card_name=self.pipline_card.name,
        )

        return viz

    def visualize(self, save: bool = False):
        viz = self._get_relationships()

        if save:
            viz.graph().render(
                cleanup=True,
                filename=self.pipline_card.name,
                format="png",
            )
        return viz.graph()
