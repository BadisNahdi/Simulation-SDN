import matplotlib.pyplot as plt
import numpy as np

def calculate_statistics(values):
    """Calculate the minimum, average, and maximum values from a list."""
    return np.min(values), np.mean(values), np.max(values)

def plot(time, latency, min_rtt, avg_rtt, max_rtt):
    """Plot latency values with statistical lines and labels."""
    plt.figure(figsize=(12, 6))
    plt.plot(time, latency, marker='o', linestyle='-', color='blue', label='Latency (ms)')

    plt.axhline(min_rtt, color='green', linestyle='--', label=f'Min RTT: {min_rtt:.2f} ms')
    plt.axhline(avg_rtt, color='orange', linestyle='--', label=f'Avg RTT: {avg_rtt:.2f} ms')
    plt.axhline(max_rtt, color='red', linestyle='--', label=f'Max RTT: {max_rtt:.2f} ms')

    plt.title('Jitter Over Time with Statistics (Server 10.0.0.4)', fontsize=14)
    plt.xlabel('Ping Sequence', fontsize=12)
    plt.ylabel('Latency (ms)', fontsize=12)
    plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()

def main():
    """Main function to calculate statistics and plot latency."""
    try:
        #change the values
        values = []
        
        time = np.arange(1, len(values) + 1)
        min_rtt, avg_rtt, max_rtt = calculate_statistics(values)
        plot(time, values, min_rtt, avg_rtt, max_rtt)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
