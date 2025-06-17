from scapy.all import *
import os
import networkx as nx
import matplotlib.pyplot as plt
import struct
from collections import defaultdict

def analyze_rpl_from_pcaps(pcap_folder):
    """Analisa arquivos pcap específicos do seu ambiente"""
    print(f"\nIniciando análise em: {pcap_folder}")
    
    # Estruturas de dados
    topology = nx.DiGraph()
    node_ranks = defaultdict(int)
    traffic_patterns = defaultdict(int)
    
    # Contadores
    total_packets = 0
    rpl_packets = 0
    
    for pcap_file in sorted(os.listdir(pcap_folder)):
        if not pcap_file.lower().endswith(('.pcap', '.pcapng')):
            continue
            
        file_path = os.path.join(pcap_folder, pcap_file)
        print(f"\nProcessando: {pcap_file}")
        
        try:
            packets = rdpcap(file_path)
            for pkt in packets:
                total_packets += 1
                
                # Verificar pacotes ICMPv6 RPL
                if pkt.haslayer('ICMPv6RPL'):
                    rpl_packets += 1
                    src = pkt['IPv6'].src.split(':')[-1]
                    dst = pkt['IPv6'].dst.split(':')[-1]
                    
                    # Registrar padrão de tráfego
                    traffic_patterns[(src, dst)] += 1
                    
                    # Determinar rank baseado no fluxo (heurística)
                    if src == '1':  # Assume-se que o nó 1 é a raiz
                        node_ranks[dst] = 512  # Rank padrão para filhos da raiz
                    elif dst == '1':
                        node_ranks[src] = 512
                    else:
                        # Se comunicação entre nós não-raiz, ajusta ranks
                        node_ranks[src] = min(node_ranks.get(src, 1024), 1024)
                        node_ranks[dst] = min(node_ranks.get(dst, 1024), 768)
                    
                    print(f"  Pacote RPL: {src} -> {dst}")

        except Exception as e:
            print(f"  Erro no arquivo {pcap_file}: {str(e)}")
            continue

    # Construir topologia baseada nos padrões de tráfego
    for (src, dst), count in traffic_patterns.items():
        topology.add_node(src, rank=node_ranks.get(src, 1024))
        topology.add_node(dst, rank=node_ranks.get(dst, 1024))
        
        # Se comunicação frequente, assume relação pai-filho
        if count > 1:
            if node_ranks.get(src, 1024) < node_ranks.get(dst, 1024):
                topology.add_edge(src, dst)
            else:
                topology.add_edge(dst, src)

    # Identificar raiz (nó com menor rank)
    if topology.nodes():
        root_node = min(topology.nodes(), key=lambda x: topology.nodes[x].get('rank', 1024))
        print(f"\nNó raiz identificado: {root_node}")

        # Visualização
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(topology)
        
        # Cores baseadas no rank
        node_colors = []
        for node in topology.nodes():
            if node == root_node:
                node_colors.append('gold')
            elif topology.nodes[node]['rank'] < 768:
                node_colors.append('lightgreen')
            else:
                node_colors.append('lightblue')
                
        nx.draw(topology, pos, with_labels=True, node_size=1500,
               node_color=node_colors, font_size=10, arrowsize=20)
        
        plt.title(f"Topologia RPL (Raiz: {root_node})", fontsize=14)
        plt.savefig('rpl_topology.png', dpi=300)
        plt.close()
        
        # Relatório
        with open('rpl_report.txt', 'w') as f:
            f.write("=== Relatório de Topologia RPL ===\n\n")
            f.write(f"Total pacotes: {total_packets}\n")
            f.write(f"Pacotes RPL: {rpl_packets}\n")
            f.write(f"Nós detectados: {len(topology.nodes())}\n\n")
            
            f.write("Hierarquia de nós:\n")
            for node in sorted(topology.nodes(), 
                              key=lambda x: topology.nodes[x]['rank']):
                f.write(f"- Nó {node} (Rank: {topology.nodes[node]['rank']})\n")
            
            f.write("\nRelações de roteamento:\n")
            for edge in topology.edges():
                f.write(f"{edge[0]} -> {edge[1]}\n")
        
        print("\nAnálise concluída com sucesso!")
        print("Arquivos gerados:")
        print("- rpl_topology.png")
        print("- rpl_report.txt")
        return True
    
    print("\nNenhum pacote RPL válido encontrado.")
    return False

if __name__ == "__main__":
    pcap_dir = r"C:\Users\Santana\Documents\sensores"
    
    if not os.path.exists(pcap_dir):
        print(f"Erro: Pasta não encontrada - {pcap_dir}")
    else:
        analyze_rpl_from_pcaps(pcap_dir)