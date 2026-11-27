# Contrato de Integração - Ambiente e Agente

Este documento define como o Agente (Patrícia) e a Interface (Helen) devem interagir com o Ambiente (José Inácio).

## 1. Como instanciar o mundo
from src.environment.world import World
mundo = World(size=4, num_wumpus=1, seed=42)

## 2. O que o Agente recebe (Percepções)
Sempre que a Patrícia for agir, ela pode chamar percepts = mundo.get_percepts().
O retorno é um dicionário com as chaves booleanas:
- breeze: True se há poço adjacente.
- stench: True se há Wumpus adjacente.
- glitter: True se o ouro está na célula atual.
- bump: True se ele tentou andar contra a parede.
- scream: True se um Wumpus morreu no último turno.

## 3. Como o Agente age
Patrícia deve chamar a função mundo.step(acao).
As ações válidas (strings) são:
- Movimento: "MOVE_UP", "MOVE_DOWN", "MOVE_LEFT", "MOVE_RIGHT"
- Ouro: "GRAB"
- Tiro: "SHOOT_UP", "SHOOT_DOWN", "SHOOT_LEFT", "SHOOT_RIGHT"
- Sair: "CLIMB" (só funciona se estiver com o ouro na posição inicial).

O retorno do step é uma tupla: (percepts, done, info).
- percepts: O que ele sentiu após a ação.
- done: True se o jogo acabou (morreu ou venceu).
- info: Dicionário com status, cause, has_gold, steps e score.

## 4. Como a Interface Gráfica (Helen) lê o mundo
Helen deve chamar mundo.get_state() para renderizar o jogo. Ela vai receber um dicionário com:
- size, agent_pos, agent_alive, has_gold, arrows
- pits, wumpus, gold_pos, done, won
