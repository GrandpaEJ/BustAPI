
import matplotlib.pyplot as plt

def generate_graph():
    # Data from latest run (approximate)
    frameworks = ['BustAPI', 'Catzilla', 'Flask', 'FastAPI', 'Robyn']
    endpoints = ['/', '/json', '/user/10']
    
    data = {
        'BustAPI': [32533, 30955, 15206],
        'Catzilla': [8748, 10045, 9705],
        'Flask': [2985, 2132, 2688],
        'FastAPI': [3254, 3624, 5235],
        'Robyn': [7589, 7568, 7269]
    }
    
    # Setup plot
    plt.figure(figsize=(12, 7))
    
    # Bar settings
    bar_width = 0.15
    opacity = 0.85
    index = [0, 1, 2]
    colors = ['#2ecc71', '#e74c3c', '#34495e', '#f1c40f', '#9b59b6']
    
    # Plot each framework
    for i, fw in enumerate(frameworks):
        plt.bar(
            [x + (i * bar_width) for x in index],
            data[fw],
            bar_width,
            alpha=opacity,
            color=colors[i],
            label=fw,
            edgecolor='white'
        )

    plt.xlabel('Endpoints', fontsize=12, fontweight='bold')
    plt.ylabel('Requests Per Second (RPS)', fontsize=12, fontweight='bold')
    plt.title('Web Framework Performance Comparison (BustAPI vs Others)', fontsize=14, fontweight='bold', pad=20)
    plt.xticks([x + (bar_width * (len(frameworks) - 1) / 2) for x in index], endpoints, fontsize=11)
    plt.yticks(fontsize=10)
    plt.legend(fontsize=10, title="Frameworks", title_fontsize=11)
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Save graph
    output_path = "benchmarks/rps_comparison.png"
    plt.savefig(output_path, dpi=300)
    print(f"✅ Graph saved to {output_path}")

if __name__ == "__main__":
    generate_graph()
