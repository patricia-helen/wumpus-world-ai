"""Entidades do Mundo de Wumpus.

Define os objetos que povoam o ambiente: poços, Wumpus, ouro
e o estado mutável do agente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

Position = Tuple[int, int]  # (linha, coluna)

@dataclass(frozen=True)
class Pit:
    """Poço: célula letal. Não se move."""
    pos: Position

@dataclass
class Wumpus:
    """Wumpus: criatura letal. Pode ser morto por flecha."""
    pos: Position
    alive: bool = True

    def kill(self) -> None:
        """Marca o Wumpus como morto."""
        self.alive = False

@dataclass(frozen=True)
class Gold:
    """Ouro: objetivo do agente."""
    pos: Position

@dataclass
class AgentState:
    """Estado mutável do agente dentro do ambiente."""
    pos: Position = (0, 0)
    alive: bool = True
    arrows: int = 1
    has_gold: bool = False
    returned_home: bool = False
    steps: int = 0

    def reset(self, start_pos: Position = (0, 0), arrows: int = 1) -> None:
        """Reinicia o agente."""
        self.pos = start_pos
        self.alive = True
        self.arrows = arrows
        self.has_gold = False
        self.returned_home = False
        self.steps = 0