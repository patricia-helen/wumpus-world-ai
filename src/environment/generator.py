"""Geração procedural segura do Mundo de Wumpus.

Regras de geração:
- Tamanho mínimo 4x4.
- Número de poços proporcional ao tamanho: max(2, int(size*size*0.15)).
- Célula inicial do agente + suas 4 vizinhas ortogonais formam a
  ZONA SEGURA: não podem conter poço nem Wumpus.
- O ouro é posicionado fora da zona segura.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Set

from .entities import Gold, Pit, Position, Wumpus

MIN_SIZE = 4
PIT_RATIO = 0.15


@dataclass
class WorldConfig:
    """Configuração completa do mundo gerado."""
    size: int
    start_pos: Position
    pits: List[Pit] = field(default_factory=list)
    wumpus: List[Wumpus] = field(default_factory=list)
    gold: Optional[Gold] = None
    arrows: int = 1

    def __repr__(self) -> str:
        return (f"WorldConfig(size={self.size}, start={self.start_pos}, "
                f"pits={len(self.pits)}, wumpus={len(self.wumpus)}, "
                f"gold={self.gold.pos if self.gold else None})")


# --------------------------------------------------------------------------
# Utilitários de vizinhança
# --------------------------------------------------------------------------

def neighbors(pos: Position, size: int) -> List[Position]:
    """Retorna os vizinhos ortogonais (cima, baixo, esq, dir) dentro do grid."""
    r, c = pos
    candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
    return [(rr, cc) for rr, cc in candidates if 0 <= rr < size and 0 <= cc < size]


def safe_zone(start: Position, size: int) -> Set[Position]:
    """Zona segura = célula inicial + vizinhos ortogonais."""
    return {start, *neighbors(start, size)}


# --------------------------------------------------------------------------
# Fórmula de poços
# --------------------------------------------------------------------------

def compute_num_pits(size: int) -> int:
    """Número de poços proporcional ao tamanho, com mínimo de 2."""
    return max(2, int(size * size * PIT_RATIO))


# --------------------------------------------------------------------------
# Geração principal
# --------------------------------------------------------------------------

def generate_world(
    size: int,
    num_wumpus: int = 1,
    num_pits: Optional[int] = None,
    start_pos: Position = (0, 0),
    seed: Optional[int] = None,
) -> WorldConfig:
    """Gera um mundo aleatório seguro."""
    if size < MIN_SIZE:
        raise ValueError(f"Tamanho mínimo é {MIN_SIZE}x{MIN_SIZE}, recebido {size}x{size}.")
    if not (0 <= start_pos[0] < size and 0 <= start_pos[1] < size):
        raise ValueError(f"start_pos {start_pos} fora do grid {size}x{size}.")

    rng = random.Random(seed)

    # Todas as células do grid
    all_cells: List[Position] = [(r, c) for r in range(size) for c in range(size)]

    # Células PROIBIDAS para poços/Wumpus (zona segura)
    forbidden: Set[Position] = safe_zone(start_pos, size)

    # Células elegíveis para poços/Wumpus (fora da zona segura)
    eligible: List[Position] = [p for p in all_cells if p not in forbidden]

    # Quantidade de poços
    if num_pits is None:
        num_pits = compute_num_pits(size)

    total_needed = num_pits + num_wumpus + 1  # +1 para o ouro
    if total_needed > len(eligible):
        raise ValueError(
            f"Grid {size}x{size} pequeno demais para {num_pits} poços, "
            f"{num_wumpus} Wumpus e 1 ouro fora da zona segura."
        )

    # Sorteia sem reposição
    rng.shuffle(eligible)

    pit_positions = eligible[:num_pits]
    wumpus_positions = eligible[num_pits:num_pits + num_wumpus]
    gold_pos = eligible[num_pits + num_wumpus]

    pits = [Pit(p) for p in pit_positions]
    wumpus = [Wumpus(p) for p in wumpus_positions]
    gold = Gold(gold_pos)

    return WorldConfig(
        size=size,
        start_pos=start_pos,
        pits=pits,
        wumpus=wumpus,
        gold=gold,
        arrows=1,
    )