import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def criar_grafo_rpl():
    # 1. Definir os dados da topologia
    nodes_data = {
        '1a': {'rank': 512},  # DODAG Root - menor rank
        '5': {'rank': 512},
        '3': {'rank': 512},
        '2': {'rank': 512},
        '10': {'rank': 768},
        '12': {'rank': 768},
        '9': {'rank': 768},
        '11': {'rank': 768},
        '4': {'rank': 768},
        '6': {'rank': 768},
        '7': {'rank': 768},
        '8': {'rank': 768},
        '1': {'rank': 1024}   # Nó folha - maior rank
    }
    
    edges_data = [
        ('1a', '1'), ('1a', '5'), ('1a', '2'), ('1a', '3'),
        ('1a', '10'), ('1a', '12'), ('1a', '9'), ('1a', '11'),
        ('1a', '4'), ('1a', '6'), ('1a', '7'), ('1a', '8'),
        ('5', '1'), ('5', '6'), ('3', '1'), ('3', '4'),
        ('2', '1'), ('2', '10'), ('2', '9'), ('10', '12'),
        ('12', '10'), ('9', '11'), ('11', '9'), ('6', '7'),
        ('7', '6'), ('7', '8'), ('8', '7')
    ]
    
    # 2. Criar o grafo direcionado
    G = nx.DiGraph()
    
    # 3. Adicionar nós com atributos
    for node, attributes in nodes_data.items():
        G.add_node(node, **attributes)
    
    # 4. Adicionar arestas
    G.add_edges_from(edges_data)
    
    # 5. Configurar visualização
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # 6. Layout manual baseado no rank
    pos = {}
    rank_levels = {512: 0, 768: 1, 1024: 2}  # Níveis verticais (Root no topo)
    
    # Organizar nós horizontalmente por nível
    for rank, y_pos in rank_levels.items():
        same_rank_nodes = [n for n in G.nodes() if G.nodes[n]['rank'] == rank]
        for i, node in enumerate(same_rank_nodes):
            pos[node] = (i - len(same_rank_nodes)/2, y_pos)
    
    # 7. Configurar cores
    cmap = LinearSegmentedColormap.from_list('rank', ['#f28e2b', '#59a14f', '#4e79a7'])  # Laranja->Verde->Azul
    node_colors = [cmap((G.nodes[node]['rank']-512)/(1024-512)) for node in G.nodes()]
    
    # 8. Desenhar nós
    nx.draw_networkx_nodes(
        G, pos,
        node_size=1800,
        node_color=node_colors,
        edgecolors='#333333',
        linewidths=1.5,
        alpha=0.9
    )
    
    # 9. Desenhar arestas
    nx.draw_networkx_edges(
        G, pos,
        width=1.5,
        edge_color='#555555',
        arrowsize=20,
        arrowstyle='-|>',
        connectionstyle='arc3,rad=0.1'
    )
    
    # 10. Adicionar rótulos
    labels = {n: f"{n}\nRank {G.nodes[n]['rank']}" for n in G.nodes()}
    nx.draw_networkx_labels(
        G, pos,
        labels,
        font_size=9,
        font_weight='bold',
        font_family='sans-serif'
    )
    
    # 11. Configurar barra de cores
    sm = plt.cm.ScalarMappable(
        cmap=cmap,
        norm=plt.Normalize(vmin=512, vmax=1024)
    )
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5, pad=0.02)
    cbar.set_label('Rank RPL', rotation=270, labelpad=15)
    
    # 12. Configurar título e layout
    ax.set_title(
        "Topologia RPL - Rede de Sensores IoT\nHierarquia de Roteamento",
        fontsize=14,
        pad=20
    )
    ax.axis('off')
    plt.tight_layout()
    
    # 13. Salvar a imagem
    plt.savefig(
        'topologia_rpl_final.png',
        dpi=300,
        bbox_inches='tight',
        transparent=False
    )
    plt.close()
    
    print("Gráfico gerado com sucesso como 'topologia_rpl_final.png'")

if __name__ == "__main__":
    criar_grafo_rpl()