"""Módulo de métricas e simulações em lote (headless).

Permite rodar partidas sem interface gráfica para testar a eficiência
do agente em larga escala.
"""

from __future__ import annotations

from typing import Callable, Dict, Any
from .world import World

def run_episode(agent: Any, world: World, max_steps: int = 1000) -> Dict[str, Any]:
    """Executa uma partida completa até o agente vencer, morrer ou estourar os passos."""
    done = False
    percepts = world.get_percepts()
    
    while not done and world.agent.steps < max_steps:
        # O agente pensa e escolhe uma ação (o Integrante 2 vai implementar isso)
        action = agent.act(percepts, world.get_state())
        
        # O mundo reage à ação
        percepts, done, info = world.step(action)
        
    return {
        "won": world.won,
        "dead": not world.agent.alive,
        "steps": world.agent.steps,
        "score": world._compute_score(),
        "cause": world.cause_of_death
    }

def run_batch(agent_factory: Callable[[], Any], n_episodes: int = 100, size: int = 4) -> Dict[str, Any]:
    """Roda várias partidas seguidas e retorna a média das métricas."""
    results = []
    for i in range(n_episodes):
        # Usa a seed para conseguir rodar simulações idênticas se precisar
        world = World(size=size, seed=i)
        agent = agent_factory()
        results.append(run_episode(agent, world))
        
    wins = sum(1 for r in results if r["won"])
    deaths = sum(1 for r in results if r["dead"])
    timeouts = n_episodes - wins - deaths
    avg_steps = sum(r["steps"] for r in results) / n_episodes
    avg_score = sum(r["score"] for r in results) / n_episodes
    
    return {
        "total_episodes": n_episodes,
        "wins": wins,
        "deaths": deaths,
        "timeouts": timeouts,
        "win_rate": wins / n_episodes,
        "death_rate": deaths / n_episodes,
        "avg_steps": avg_steps,
        "avg_score": avg_score
    }