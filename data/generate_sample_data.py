"""
Generate sample network flow data for the AI-Driven IDS demo.
Creates realistic network traffic data with both normal and attack patterns.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_network_flow_data(n_samples=10000, attack_ratio=0.1):
    """
    Generate synthetic network flow data with normal and attack patterns.
    
    Args:
        n_samples: Total number of samples to generate
        attack_ratio: Ratio of attack samples to normal samples
    
    Returns:
        DataFrame with network flow features
    """
    np.random.seed(42)
    random.seed(42)
    
    n_attacks = int(n_samples * attack_ratio)
    n_normal = n_samples - n_attacks
    
    # Normal traffic patterns
    normal_data = []
    for _ in range(n_normal):
        flow = {
            'duration': np.random.exponential(10),  # seconds
            'protocol_type': random.choice(['tcp', 'udp', 'icmp']),
            'service': random.choice(['http', 'ftp', 'smtp', 'ssh', 'dns', 'pop3']),
            'flag': random.choice(['SF', 'S0', 'REJ', 'RSTR', 'RSTO', 'S1', 'S2', 'S3']),
            'src_bytes': np.random.lognormal(8, 2),
            'dst_bytes': np.random.lognormal(8, 2),
            'land': 0,  # No land attacks in normal traffic
            'wrong_fragment': 0,
            'urgent': 0,
            'hot': np.random.poisson(1),
            'num_failed_logins': 0,
            'logged_in': 1,
            'num_compromised': 0,
            'root_shell': 0,
            'su_attempted': 0,
            'num_root': 0,
            'num_file_creations': np.random.poisson(1),
            'num_shells': 0,
            'num_access_files': np.random.poisson(2),
            'num_outbound_cmds': 0,
            'is_host_login': 0,
            'is_guest_login': 0,
            'count': np.random.poisson(5),
            'srv_count': np.random.poisson(3),
            'serror_rate': np.random.beta(1, 9),
            'srv_serror_rate': np.random.beta(1, 9),
            'rerror_rate': np.random.beta(1, 9),
            'srv_rerror_rate': np.random.beta(1, 9),
            'same_srv_rate': np.random.beta(8, 2),
            'diff_srv_rate': np.random.beta(2, 8),
            'srv_diff_host_rate': np.random.beta(2, 8),
            'dst_host_count': np.random.poisson(10),
            'dst_host_srv_count': np.random.poisson(5),
            'dst_host_same_srv_rate': np.random.beta(8, 2),
            'dst_host_diff_srv_rate': np.random.beta(2, 8),
            'dst_host_same_src_port_rate': np.random.beta(8, 2),
            'dst_host_srv_diff_host_rate': np.random.beta(2, 8),
            'dst_host_serror_rate': np.random.beta(1, 9),
            'dst_host_srv_serror_rate': np.random.beta(1, 9),
            'dst_host_rerror_rate': np.random.beta(1, 9),
            'dst_host_srv_rerror_rate': np.random.beta(1, 9),
            'label': 'normal'
        }
        normal_data.append(flow)
    
    # Attack patterns (simplified)
    attack_types = ['dos', 'probe', 'r2l', 'u2r']
    attack_data = []
    
    for _ in range(n_attacks):
        attack_type = random.choice(attack_types)
        
        if attack_type == 'dos':  # Denial of Service
            flow = {
                'duration': np.random.exponential(0.1),  # Very short
                'protocol_type': random.choice(['tcp', 'udp']),
                'service': random.choice(['http', 'ftp']),
                'flag': random.choice(['S0', 'REJ']),
                'src_bytes': np.random.lognormal(6, 1),
                'dst_bytes': 0,  # No response
                'land': 0,
                'wrong_fragment': 0,
                'urgent': 0,
                'hot': np.random.poisson(10),  # High
                'num_failed_logins': 0,
                'logged_in': 0,
                'num_compromised': 0,
                'root_shell': 0,
                'su_attempted': 0,
                'num_root': 0,
                'num_file_creations': 0,
                'num_shells': 0,
                'num_access_files': 0,
                'num_outbound_cmds': 0,
                'is_host_login': 0,
                'is_guest_login': 0,
                'count': np.random.poisson(50),  # High connection count
                'srv_count': np.random.poisson(30),
                'serror_rate': np.random.beta(8, 2),  # High error rate
                'srv_serror_rate': np.random.beta(8, 2),
                'rerror_rate': np.random.beta(8, 2),
                'srv_rerror_rate': np.random.beta(8, 2),
                'same_srv_rate': np.random.beta(9, 1),
                'diff_srv_rate': np.random.beta(1, 9),
                'srv_diff_host_rate': np.random.beta(1, 9),
                'dst_host_count': np.random.poisson(100),
                'dst_host_srv_count': np.random.poisson(50),
                'dst_host_same_srv_rate': np.random.beta(9, 1),
                'dst_host_diff_srv_rate': np.random.beta(1, 9),
                'dst_host_same_src_port_rate': np.random.beta(9, 1),
                'dst_host_srv_diff_host_rate': np.random.beta(1, 9),
                'dst_host_serror_rate': np.random.beta(8, 2),
                'dst_host_srv_serror_rate': np.random.beta(8, 2),
                'dst_host_rerror_rate': np.random.beta(8, 2),
                'dst_host_srv_rerror_rate': np.random.beta(8, 2),
                'label': 'dos'
            }
        
        elif attack_type == 'probe':  # Probing/Scanning
            flow = {
                'duration': np.random.exponential(5),
                'protocol_type': 'tcp',
                'service': random.choice(['http', 'ftp', 'smtp', 'ssh']),
                'flag': random.choice(['S0', 'REJ', 'RSTR']),
                'src_bytes': np.random.lognormal(7, 1),
                'dst_bytes': 0,
                'land': 0,
                'wrong_fragment': 0,
                'urgent': 0,
                'hot': np.random.poisson(5),
                'num_failed_logins': 0,
                'logged_in': 0,
                'num_compromised': 0,
                'root_shell': 0,
                'su_attempted': 0,
                'num_root': 0,
                'num_file_creations': 0,
                'num_shells': 0,
                'num_access_files': 0,
                'num_outbound_cmds': 0,
                'is_host_login': 0,
                'is_guest_login': 0,
                'count': np.random.poisson(20),
                'srv_count': np.random.poisson(15),
                'serror_rate': np.random.beta(6, 4),
                'srv_serror_rate': np.random.beta(6, 4),
                'rerror_rate': np.random.beta(6, 4),
                'srv_rerror_rate': np.random.beta(6, 4),
                'same_srv_rate': np.random.beta(7, 3),
                'diff_srv_rate': np.random.beta(3, 7),
                'srv_diff_host_rate': np.random.beta(3, 7),
                'dst_host_count': np.random.poisson(50),
                'dst_host_srv_count': np.random.poisson(25),
                'dst_host_same_srv_rate': np.random.beta(7, 3),
                'dst_host_diff_srv_rate': np.random.beta(3, 7),
                'dst_host_same_src_port_rate': np.random.beta(7, 3),
                'dst_host_srv_diff_host_rate': np.random.beta(3, 7),
                'dst_host_serror_rate': np.random.beta(6, 4),
                'dst_host_srv_serror_rate': np.random.beta(6, 4),
                'dst_host_rerror_rate': np.random.beta(6, 4),
                'dst_host_srv_rerror_rate': np.random.beta(6, 4),
                'label': 'probe'
            }
        
        elif attack_type == 'r2l':  # Remote to Local
            flow = {
                'duration': np.random.exponential(15),
                'protocol_type': 'tcp',
                'service': random.choice(['ftp', 'smtp', 'ssh', 'pop3']),
                'flag': 'SF',
                'src_bytes': np.random.lognormal(9, 2),
                'dst_bytes': np.random.lognormal(8, 2),
                'land': 0,
                'wrong_fragment': 0,
                'urgent': 0,
                'hot': np.random.poisson(2),
                'num_failed_logins': np.random.poisson(3),  # Multiple failed attempts
                'logged_in': 1,
                'num_compromised': 0,
                'root_shell': 0,
                'su_attempted': 0,
                'num_root': 0,
                'num_file_creations': np.random.poisson(2),
                'num_shells': 0,
                'num_access_files': np.random.poisson(5),
                'num_outbound_cmds': 0,
                'is_host_login': 0,
                'is_guest_login': 0,
                'count': np.random.poisson(3),
                'srv_count': np.random.poisson(2),
                'serror_rate': np.random.beta(3, 7),
                'srv_serror_rate': np.random.beta(3, 7),
                'rerror_rate': np.random.beta(3, 7),
                'srv_rerror_rate': np.random.beta(3, 7),
                'same_srv_rate': np.random.beta(8, 2),
                'diff_srv_rate': np.random.beta(2, 8),
                'srv_diff_host_rate': np.random.beta(2, 8),
                'dst_host_count': np.random.poisson(5),
                'dst_host_srv_count': np.random.poisson(3),
                'dst_host_same_srv_rate': np.random.beta(8, 2),
                'dst_host_diff_srv_rate': np.random.beta(2, 8),
                'dst_host_same_src_port_rate': np.random.beta(8, 2),
                'dst_host_srv_diff_host_rate': np.random.beta(2, 8),
                'dst_host_serror_rate': np.random.beta(3, 7),
                'dst_host_srv_serror_rate': np.random.beta(3, 7),
                'dst_host_rerror_rate': np.random.beta(3, 7),
                'dst_host_srv_rerror_rate': np.random.beta(3, 7),
                'label': 'r2l'
            }
        
        else:  # u2r - User to Root
            flow = {
                'duration': np.random.exponential(20),
                'protocol_type': 'tcp',
                'service': 'ssh',
                'flag': 'SF',
                'src_bytes': np.random.lognormal(10, 2),
                'dst_bytes': np.random.lognormal(9, 2),
                'land': 0,
                'wrong_fragment': 0,
                'urgent': 0,
                'hot': np.random.poisson(3),
                'num_failed_logins': np.random.poisson(5),
                'logged_in': 1,
                'num_compromised': 1,
                'root_shell': 1,
                'su_attempted': 1,
                'num_root': 1,
                'num_file_creations': np.random.poisson(3),
                'num_shells': 1,
                'num_access_files': np.random.poisson(8),
                'num_outbound_cmds': 1,
                'is_host_login': 0,
                'is_guest_login': 0,
                'count': np.random.poisson(2),
                'srv_count': np.random.poisson(1),
                'serror_rate': np.random.beta(2, 8),
                'srv_serror_rate': np.random.beta(2, 8),
                'rerror_rate': np.random.beta(2, 8),
                'srv_rerror_rate': np.random.beta(2, 8),
                'same_srv_rate': np.random.beta(9, 1),
                'diff_srv_rate': np.random.beta(1, 9),
                'srv_diff_host_rate': np.random.beta(1, 9),
                'dst_host_count': np.random.poisson(3),
                'dst_host_srv_count': np.random.poisson(2),
                'dst_host_same_srv_rate': np.random.beta(9, 1),
                'dst_host_diff_srv_rate': np.random.beta(1, 9),
                'dst_host_same_src_port_rate': np.random.beta(9, 1),
                'dst_host_srv_diff_host_rate': np.random.beta(1, 9),
                'dst_host_serror_rate': np.random.beta(2, 8),
                'dst_host_srv_serror_rate': np.random.beta(2, 8),
                'dst_host_rerror_rate': np.random.beta(2, 8),
                'dst_host_srv_rerror_rate': np.random.beta(2, 8),
                'label': 'u2r'
            }
        
        attack_data.append(flow)
    
    # Combine and shuffle data
    all_data = normal_data + attack_data
    random.shuffle(all_data)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Add timestamp
    start_time = datetime.now() - timedelta(days=7)
    df['timestamp'] = [start_time + timedelta(seconds=i*60) for i in range(len(df))]
    
    return df

def split_data_for_federated(df, n_clients=3):
    """
    Split data for federated learning simulation.
    Each client gets a different distribution of attack types.
    """
    # Split by attack types to simulate different client environments
    normal_data = df[df['label'] == 'normal']
    dos_data = df[df['label'] == 'dos']
    probe_data = df[df['label'] == 'probe']
    r2l_data = df[df['label'] == 'r2l']
    u2r_data = df[df['label'] == 'u2r']
    
    # Create different distributions for each client
    client_data = []
    
    # Client 1: Mostly normal + some DoS attacks (corporate network)
    client1 = pd.concat([
        normal_data.sample(frac=0.4, random_state=1),
        dos_data.sample(frac=0.8, random_state=1),
        probe_data.sample(frac=0.2, random_state=1)
    ]).sample(frac=1, random_state=1)
    client_data.append(client1)
    
    # Client 2: Normal + probing attacks (research network)
    client2 = pd.concat([
        normal_data.sample(frac=0.35, random_state=2),
        probe_data.sample(frac=0.7, random_state=2),
        r2l_data.sample(frac=0.6, random_state=2)
    ]).sample(frac=1, random_state=2)
    client_data.append(client2)
    
    # Client 3: Normal + privilege escalation (server farm)
    client3 = pd.concat([
        normal_data.sample(frac=0.25, random_state=3),
        u2r_data.sample(frac=0.9, random_state=3),
        r2l_data.sample(frac=0.4, random_state=3),
        dos_data.sample(frac=0.2, random_state=3)
    ]).sample(frac=1, random_state=3)
    client_data.append(client3)
    
    return client_data

def save_datasets():
    """Generate and save all datasets."""
    print("Generating sample network flow data...")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Generate main dataset
    df = generate_network_flow_data(n_samples=10000, attack_ratio=0.15)
    df.to_csv('data/network_flows.csv', index=False)
    print(f"Saved main dataset: {len(df)} samples")
    
    # Generate federated client datasets
    client_data = split_data_for_federated(df, n_clients=3)
    for i, client_df in enumerate(client_data):
        client_df.to_csv(f'data/client_{i+1}_data.csv', index=False)
        print(f"Saved client {i+1} data: {len(client_df)} samples")
    
    # Generate test dataset
    test_df = generate_network_flow_data(n_samples=2000, attack_ratio=0.2)
    test_df.to_csv('data/test_data.csv', index=False)
    print(f"Saved test dataset: {len(test_df)} samples")
    
    # Print data distribution
    print("\nData distribution:")
    print(df['label'].value_counts())
    
    print("\nClient data distributions:")
    for i, client_df in enumerate(client_data):
        print(f"Client {i+1}: {client_df['label'].value_counts().to_dict()}")

if __name__ == "__main__":
    save_datasets()
