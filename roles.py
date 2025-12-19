"""
Role Detection Module

This module implements the role detection algorithm based on Non-negative Matrix Factorization (NMF)
as described in the paper "Defining and Allocating Roles" section.

The algorithm:
1. Divides the playing area into 5m x 5m bins
2. Creates player count matrices by counting observations in each bin
3. Normalizes to create player occupancy matrices (removes time-on-pitch effect)
4. Applies Gaussian smoothing to reduce noise
5. Uses NMF with KL divergence to decompose X ≈ WB
   - B: basis matrix (defines the roles)
   - W: weight matrix (contribution of each role to each player)
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter
from sklearn.decomposition import NMF


def create_player_count_matrix(xy_data: np.ndarray,
                               pitch_xlim: tuple,
                               pitch_ylim: tuple,
                               bin_size: float = 5.0) -> np.ndarray:
    """
    Create a count matrix for a single player by counting observations in each bin.
    
    Parameters
    ----------
    xy_data : np.ndarray
        Array of shape (T, 2) containing x, y coordinates for a player over T time frames.
    pitch_xlim : tuple
        Tuple (x_min, x_max) defining the pitch x-axis limits in meters.
    pitch_ylim : tuple
        Tuple (y_min, y_max) defining the pitch y-axis limits in meters.
    bin_size : float
        Size of each bin in meters (default 5.0m).
        
    Returns
    -------
    count_matrix : np.ndarray
        2D array of shape (n_bins_y, n_bins_x) containing counts per bin.
    """
    x_min, x_max = pitch_xlim
    y_min, y_max = pitch_ylim

    # Calculate number of bins
    n_bins_x = int(np.ceil((x_max - x_min) / bin_size))
    n_bins_y = int(np.ceil((y_max - y_min) / bin_size))

    # Initialize count matrix
    count_matrix = np.zeros((n_bins_y, n_bins_x))

    # Filter out NaN values
    valid_mask = ~np.isnan(xy_data[:, 0]) & ~np.isnan(xy_data[:, 1])
    xy_valid = xy_data[valid_mask]

    if len(xy_valid) == 0:
        return count_matrix

    # Calculate bin indices for each observation
    x_bins = np.clip(((xy_valid[:, 0] - x_min) / bin_size).astype(int), 0, n_bins_x - 1)
    y_bins = np.clip(((xy_valid[:, 1] - y_min) / bin_size).astype(int), 0, n_bins_y - 1)

    # Count observations in each bin
    for x_bin, y_bin in zip(x_bins, y_bins):
        count_matrix[y_bin, x_bin] += 1

    return count_matrix


def normalize_to_occupancy(count_matrix: np.ndarray) -> np.ndarray:
    """
    Normalize count matrix to unit sum to create player occupancy matrix.
    This removes the effect of variations in playing time (time-on-pitch).
    
    Parameters
    ----------
    count_matrix : np.ndarray
        2D array containing counts per bin.
        
    Returns
    -------
    occupancy_matrix : np.ndarray
        Normalized matrix with unit sum (or zeros if total count is zero).
    """
    total = count_matrix.sum()
    if total > 0:
        return count_matrix / total
    return count_matrix


def smooth_occupancy(occupancy_matrix: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """
    Apply Gaussian smoothing to reduce noise from small sample size and arbitrary binning.
    
    Parameters
    ----------
    occupancy_matrix : np.ndarray
        2D occupancy matrix for a player.
    sigma : float
        Standard deviation for Gaussian kernel (default 1.0).
        
    Returns
    -------
    smoothed_matrix : np.ndarray
        Smoothed occupancy matrix, re-normalized to unit sum.
    """
    smoothed = gaussian_filter(occupancy_matrix, sigma=sigma)
    # Re-normalize after smoothing
    total = smoothed.sum()
    if total > 0:
        smoothed = smoothed / total
    return smoothed


def build_occupancy_matrix(xy_data: np.ndarray,
                           pitch_xlim: tuple,
                           pitch_ylim: tuple,
                           bin_size: float = 5.0,
                           sigma: float = 1.0) -> tuple:
    """
    Build the full occupancy matrix X ∈ R^{N x L} from player coordinate data.
    
    Parameters
    ----------
    xy_data : np.ndarray
        Array of shape (T, N*2) where T is number of time frames and N is number of players.
        Columns alternate between x and y coordinates for each player.
    pitch_xlim : tuple
        Tuple (x_min, x_max) defining the pitch x-axis limits.
    pitch_ylim : tuple
        Tuple (y_min, y_max) defining the pitch y-axis limits.
    bin_size : float
        Size of each bin in meters (default 5.0m).
    sigma : float
        Standard deviation for Gaussian smoothing (default 1.0).
        
    Returns
    -------
    X : np.ndarray
        Occupancy matrix of shape (N, L) where N is number of players and L is number of bins.
    grid_shape : tuple
        Shape of the spatial grid (n_bins_y, n_bins_x).
    """
    n_players = xy_data.shape[1] // 2

    x_min, x_max = pitch_xlim
    y_min, y_max = pitch_ylim
    n_bins_x = int(np.ceil((x_max - x_min) / bin_size))
    n_bins_y = int(np.ceil((y_max - y_min) / bin_size))
    L = n_bins_x * n_bins_y

    X = np.zeros((n_players, L))

    for player_idx in range(n_players):
        # Extract x, y coordinates for this player
        x_col = player_idx * 2
        y_col = player_idx * 2 + 1
        player_xy = xy_data[:, [x_col, y_col]]

        # Create count matrix
        count_matrix = create_player_count_matrix(player_xy, pitch_xlim, pitch_ylim, bin_size)

        # Normalize to occupancy
        occupancy_matrix = normalize_to_occupancy(count_matrix)

        # Apply Gaussian smoothing
        smoothed_matrix = smooth_occupancy(occupancy_matrix, sigma=sigma)

        # Flatten and store in X
        X[player_idx, :] = smoothed_matrix.flatten()

    return X, (n_bins_y, n_bins_x)


def fit_nmf_roles(X: np.ndarray,
                  n_roles: int = 10,
                  max_iter: int = 500,
                  random_state: int = 42) -> tuple:
    """
    Apply NMF to decompose the occupancy matrix X ≈ WB.
    
    Uses Kullback-Leibler divergence as the objective function,
    minimized using the multiplicative update method.
    
    Parameters
    ----------
    X : np.ndarray
        Occupancy matrix of shape (N, L).
    n_roles : int
        Number of latent roles K (default 10).
    max_iter : int
        Maximum number of iterations for NMF (default 500).
    random_state : int
        Random seed for reproducibility.
        
    Returns
    -------
    W : np.ndarray
        Weight matrix of shape (N, K) - contribution of each role to each player.
    B : np.ndarray
        Basis matrix of shape (K, L) - the role definitions.
    X_reconstructed : np.ndarray
        Reconstructed occupancy matrix X̃ = WB.
    model : NMF
        Fitted NMF model.
    """
    # Add small epsilon to avoid zeros (required for KL divergence)
    X_safe = X + 1e-10

    # Initialize and fit NMF with KL divergence
    model = NMF(
        n_components=n_roles,
        init='nndsvda',  # Better for sparse data
        solver='mu',  # Multiplicative update
        beta_loss='kullback-leibler',  # KL divergence
        max_iter=max_iter,
        random_state=random_state
    )

    W = model.fit_transform(X_safe)
    B = model.components_

    # Reconstruct the matrix
    X_reconstructed = W @ B

    return W, B, X_reconstructed, model


def extract_roles(xy_data: np.ndarray,
                  pitch_xlim: tuple = (0, 105),
                  pitch_ylim: tuple = (0, 68),
                  bin_size: float = 5.0,
                  sigma: float = 1.0,
                  n_roles: int = 10,
                  max_iter: int = 500,
                  random_state: int = 42) -> dict:
    """
    Main function to extract latent roles from player coordinate data.
    
    This implements the methodology from Section 3 "Defining and Allocating Roles":
    1. Divide playing area into bins (default 5m x 5m)
    2. Count player observations per bin
    3. Normalize to occupancy matrices
    4. Apply Gaussian smoothing
    5. Decompose using NMF with KL divergence
    
    Parameters
    ----------
    xy_data : np.ndarray
        Array of shape (T, N*2) with player coordinates.
        Columns alternate x, y for each player.
    pitch_xlim : tuple
        Pitch x-axis limits in meters (default (0, 105) for standard pitch).
    pitch_ylim : tuple
        Pitch y-axis limits in meters (default (0, 68) for standard pitch).
    bin_size : float
        Size of spatial bins in meters (default 5.0).
    sigma : float
        Gaussian smoothing parameter (default 1.0).
    n_roles : int
        Number of latent roles to extract (default 10).
    max_iter : int
        Maximum NMF iterations (default 500).
    random_state : int
        Random seed for reproducibility.
        
    Returns
    -------
    results : dict
        Dictionary containing:
        - 'W': Weight matrix (N, K) - role contributions per player
        - 'B': Basis matrix (K, L) - role definitions
        - 'X': Original occupancy matrix (N, L)
        - 'X_reconstructed': Reconstructed matrix (N, L)
        - 'grid_shape': Shape of spatial grid (n_bins_y, n_bins_x)
        - 'n_players': Number of players
        - 'n_roles': Number of roles
        - 'n_bins': Total number of bins (L)
        - 'reconstruction_error': NMF reconstruction error
        - 'player_role_assignments': Dominant role for each player
    """
    # Build occupancy matrix
    X, grid_shape = build_occupancy_matrix(
        xy_data, pitch_xlim, pitch_ylim, bin_size, sigma
    )

    # Fit NMF
    W, B, X_reconstructed, model = fit_nmf_roles(
        X, n_roles, max_iter, random_state
    )

    # Get dominant role for each player
    player_role_assignments = np.argmax(W, axis=1)

    results = {
        'W': W,
        'B': B,
        'X': X,
        'X_reconstructed': X_reconstructed,
        'grid_shape': grid_shape,
        'n_players': X.shape[0],
        'n_roles': n_roles,
        'n_bins': X.shape[1],
        'reconstruction_error': model.reconstruction_err_,
        'player_role_assignments': player_role_assignments
    }

    return results


def get_role_heatmaps(B: np.ndarray, grid_shape: tuple, threshold: float | None = None, 
                       top_k: int | None = None, percentile: float | None = None) -> list:
    """
    Convert the basis matrix rows to 2D heatmaps for visualization.
    
    Parameters
    ----------
    B : np.ndarray
        Basis matrix of shape (K, L).
    grid_shape : tuple
        Shape of the spatial grid (n_bins_y, n_bins_x).
    threshold : float, optional
        Absolute threshold - values below this will be set to NaN (for transparency).
    top_k : int, optional
        Keep only the top k highest values per heatmap, rest set to NaN.
    percentile : float, optional
        Keep only values above this percentile (0-100), rest set to NaN.
        
    Returns
    -------
    heatmaps : list
        List of K 2D arrays, each representing a role's spatial distribution.
        Low values are set to NaN for transparency when using colormaps with set_bad().
    """
    n_roles = B.shape[0]
    heatmaps = []
    for k in range(n_roles):
        heatmap = B[k, :].reshape(grid_shape).copy()
        
        # Apply thresholding to show only significant values
        if top_k is not None:
            # Keep only top_k values
            flat = heatmap.flatten()
            if top_k < len(flat):
                threshold_val = np.partition(flat, -top_k)[-top_k]
                heatmap[heatmap < threshold_val] = np.nan
        elif percentile is not None:
            # Keep values above percentile
            threshold_val = np.percentile(heatmap[heatmap > 0], percentile) if np.any(heatmap > 0) else 0
            heatmap[heatmap < threshold_val] = np.nan
        elif threshold is not None:
            # Use absolute threshold
            heatmap[heatmap < threshold] = np.nan
        
        heatmaps.append(heatmap)
    return heatmaps


def get_player_role_weights(W: np.ndarray, player_idx: int) -> np.ndarray:
    """
    Get the role weights for a specific player.
    
    Parameters
    ----------
    W : np.ndarray
        Weight matrix of shape (N, K).
    player_idx : int
        Index of the player.
        
    Returns
    -------
    weights : np.ndarray
        Array of shape (K,) with role weights for the player.
    """
    return W[player_idx, :]


if __name__ == "__main__":
    # Example usage with synthetic data
    print("Role Detection Module")
    print("=" * 50)
    print("\nThis module provides functions to extract latent player roles")
    print("from positional tracking data using NMF.")
    print("\nMain function: extract_roles(xy_data, ...)")
    print("\nExample usage:")
    print("  from roles import extract_roles")
    print("  results = extract_roles(XY, pitch_xlim=(0, 105), pitch_ylim=(0, 68))")
    print("  W = results['W']  # Player role weights")
    print("  B = results['B']  # Role definitions")
