"""Motor principal do Mundo de Wumpus.

Gerencia o estado, valida ações do agente, emite percepções e
controla a morte/vitória.
"""

from __future__ import annotations

from typing import Dict, Tuple

from .entities import AgentState, Gold, Pit, Position, Wumpus
from .generator import generate_world

# Ações válidas que o agente pode tomar
VALID_ACTIONS = {
    "MOVE_UP", "MOVE_DOWN", "MOVE_LEFT", "MOVE_RIGHT",
    "GRAB", "SHOOT_UP", "SHOOT_DOWN", "SHOOT_LEFT", "SHOOT_RIGHT",
    "CLIMB"
}

class World:
    def __init__(self, size: int = 4, num_wumpus: int = 1,
                 num_pits: int | None = None, seed: int | None = None):
        """Inicializa o mundo."""
        self.size = size
        self.config = generate_world(size=size, num_wumpus=num_wumpus,
                                     num_pits=num_pits, seed=seed)
        
        self.pits = self.config.pits
        self.wumpus = self.config.wumpus
        self.gold: Gold | None = self.config.gold
        
        self.agent = AgentState(pos=self.config.start_pos, arrows=self.config.arrows)
        
        self.done = False
        self.won = False
        self.cause_of_death = None
        
        # Memória de eventos do último turno
        self.last_percepts = {}
        self.scream = False
        self.bump = False

    # ------------------------------------------------------------------
    # Sensores (Percepções)
    # ------------------------------------------------------------------
    def _get_neighbors(self, pos: Position) -> list[Position]:
        r, c = pos
        candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [(rr, cc) for rr, cc in candidates if 0 <= rr < self.size and 0 <= cc < self.size]

    def get_percepts(self) -> Dict[str, bool]:
        """Retorna o que o agente está sentindo na posição atual."""
        if not self.agent.alive or self.done:
            return {}

        pos = self.agent.pos
        vizinhos = self._get_neighbors(pos)

        # Verifica poços e Wumpus nos vizinhos
        breeze = any(p.pos in vizinhos for p in self.pits)
        stench = any(w.pos in vizinhos and w.alive for w in self.wumpus)
        
        # Verifica ouro na posição atual
        glitter = self.gold is not None and self.gold.pos == pos

        percepts = {
            "breeze": breeze,
            "stench": stench,
            "glitter": glitter,
            "bump": self.bump,
            "scream": self.scream
        }
        
        # Reseta os eventos passageiros APÓS enviar para o agente
        self.bump = False
        self.scream = False
        
        return percepts

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def step(self, action: str) -> Tuple[Dict[str, bool], bool, Dict]:
        """Executa uma ação e atualiza o estado do mundo."""
        if not self.agent.alive or self.done:
            return {}, True, {"status": "game_over", "cause": self.cause_of_death}

        if action not in VALID_ACTIONS:
            raise ValueError(f"Ação inválida: {action}")

        self.agent.steps += 1

        # Mover
        if action.startswith("MOVE_"):
            self._handle_move(action)
        
        # Pegar ouro
        elif action == "GRAB":
            if self.gold is not None and self.gold.pos == self.agent.pos:
                self.agent.has_gold = True
                self.gold = None  # Ouro sumiu do mapa

        # Atirar flecha
        elif action.startswith("SHOOT_"):
            self._handle_shoot(action)

        # Sair (Climb)
        elif action == "CLIMB":
            if self.agent.has_gold and self.agent.pos == self.config.start_pos:
                self.won = True
                self.done = True
                self.agent.returned_home = True

        # Atualiza status
        if not self.agent.alive:
            self.done = True

        info = {
            "status": "running",
            "cause": self.cause_of_death,
            "has_gold": self.agent.has_gold,
            "steps": self.agent.steps,
            "score": self._compute_score()
        }

        if self.done:
            info["status"] = "won" if self.won else "dead"

        return self.get_percepts(), self.done, info

    def _handle_move(self, action: str):
        r, c = self.agent.pos
        nr, nc = r, c
        if action == "MOVE_UP": nr -= 1
        elif action == "MOVE_DOWN": nr += 1
        elif action == "MOVE_LEFT": nc -= 1
        elif action == "MOVE_RIGHT": nc += 1

        # Bateu na parede (bump)
        if not (0 <= nr < self.size and 0 <= nc < self.size):
            self.bump = True
            return

        new_pos = (nr, nc)
        
        # Caiu no poço?
        if any(p.pos == new_pos for p in self.pits):
            self.agent.alive = False
            self.cause_of_death = "pit"
            return

        # Andou para cima do Wumpus?
        if any(w.pos == new_pos and w.alive for w in self.wumpus):
            self.agent.alive = False
            self.cause_of_death = "wumpus"
            return

        # Movimento seguro
        self.agent.pos = new_pos

    def _handle_shoot(self, action: str):
        if self.agent.arrows <= 0:
            return  # Sem flechas, ação falha
        
        self.agent.arrows -= 1
        r, c = self.agent.pos
        
        # Direção do tiro
        dr, dc = 0, 0
        if action == "SHOOT_UP": dr = -1
        elif action == "SHOOT_DOWN": dr = 1
        elif action == "SHOOT_LEFT": dc = -1
        elif action == "SHOOT_RIGHT": dc = 1

        # A flecha voa até bater na parede
        while True:
            r += dr
            c += dc
            if not (0 <= r < self.size and 0 <= c < self.size):
                break  # Bateu na parede
            
            # Acertou um Wumpus?
            hit = False
            for w in self.wumpus:
                if w.pos == (r, c) and w.alive:
                    w.kill()
                    self.scream = True
                    hit = True
                    break
            if hit:
                break  # A flecha para ao acertar

    def _compute_score(self) -> int:
        """Cálculo simples de pontuação."""
        if not self.agent.alive:
            return -1000
        score = -self.agent.steps  # -1 por passo
        if self.agent.has_gold:
            score += 1000
        if self.won:
            score += 500
        return score

    # ------------------------------------------------------------------
    # Interface para a UI
    # ------------------------------------------------------------------
    def get_state(self) -> dict:
        """Retorna o estado completo do mundo para renderização."""
        return {
            "size": self.size,
            "agent_pos": self.agent.pos,
            "agent_alive": self.agent.alive,
            "has_gold": self.agent.has_gold,
            "arrows": self.agent.arrows,
            "pits": [p.pos for p in self.pits],
            "wumpus": [w.pos for w in self.wumpus if w.alive],
            "gold_pos": self.gold.pos if self.gold else None,
            "done": self.done,
            "won": self.won
        }
    def reset(self, seed: int | None = None) -> None:
        """Reinicia o mundo, criando um novo mapa e restaurando o agente."""
        # Recria o mapa (gera novos poços, Wumpus e ouro)
        self.config = generate_world(size=self.size, num_wumpus=len(self.wumpus),
                                     num_pits=len(self.pits), seed=seed)
        
        self.pits = self.config.pits
        self.wumpus = self.config.wumpus
        self.gold = self.config.gold
        
        # Reseta o agente para a posição inicial
        self.agent.reset(start_pos=self.config.start_pos, arrows=self.config.arrows)
        
        # Reseta os status da partida
        self.done = False
        self.won = False
        self.cause_of_death = None
        self.bump = False
        self.scream = False