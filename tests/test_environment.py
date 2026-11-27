import pytest
from src.environment.generator import generate_world, safe_zone, MIN_SIZE
from src.environment.world import World

def test_min_size_enforced():
    """Garante que o gerador não aceita tabuleiros menores que 4x4."""
    with pytest.raises(ValueError):
        generate_world(size=3)

def test_start_zone_is_safe():
    """Garante que a casa inicial e seus vizinhos nunca têm poço ou Wumpus."""
    for seed in range(50):  # Testa 50 mundos diferentes
        w = generate_world(size=4, seed=seed)
        zona = safe_zone(w.start_pos, w.size)
        
        for pit in w.pits:
            assert pit.pos not in zona, f"Poço na zona segura! Seed: {seed}"
            
        for wumpus in w.wumpus:
            assert wumpus.pos not in zona, f"Wumpus na zona segura! Seed: {seed}"

def test_pit_kills_agent():
    """Garante que o agente morre se pisar em um poço."""
    world = World(size=4, seed=42)
    # Força um poço na posição (1,0) para testar o movimento DOWN
    from src.environment.entities import Pit
    world.pits = [Pit((1, 0))]
    world.wumpus = [] # Tira o wumpus para não dar conflito
    
    _, done, info = world.step("MOVE_DOWN")
    assert done is True
    assert world.agent.alive is False
    assert world.cause_of_death == "pit"

def test_shoot_kills_wumpus():
    """Garante que atirar na direção do Wumpus o mata e emite o grito."""
    world = World(size=4, seed=42)
    # Força um Wumpus na posição (0,2) para testar o tiro pra direita
    from src.environment.entities import Wumpus
    world.wumpus = [Wumpus((0, 2))]
    
    # Agora nós guardamos a percepção que o step retorna!
    percepts, done, info = world.step("SHOOT_RIGHT")
    
    assert world.wumpus[0].alive is False
    assert percepts.get("scream") is True  # <-- AQUI ESTÁ A CORREÇÃO
    assert world.agent.arrows == 0