import numpy as np
import plotly.express as px

def pca_plot(X, y, ndim=2):
    """
    Apply PCA using SVD and plot the data.

    Parameters
    ----------
    X : array-like
        Feature matrix of shape (n_samples, n_features)
    y : array-like
        Discrete labels of shape (n_samples,)
    ndim : int
        Number of PCA dimensions. Must be 2 or 3.
    """

    if ndim not in [2, 3]:
        raise ValueError("ndim must be 2 or 3")

    X = np.asarray(X)
    y = np.asarray(y)

    # Center X
    X_centered = X - X.mean(axis=0)

    # SVD
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

    # Project onto first ndim principal components
    X_pca = X_centered @ Vt[:ndim].T

    # Percentage of information retained
    info_retained = (np.sum(S[:ndim] ** 2) / np.sum(S ** 2)) * 100
    print(f"Information retained: {info_retained:.2f}%")

    # Create dataframe for Plotly
    data = {
        f"PC{i+1}": X_pca[:, i]
        for i in range(ndim)
    }
    data["Label"] = y.astype(str)

    # Plot
    if ndim == 2:
        fig = px.scatter(
            data,
            x="PC1",
            y="PC2",
            color="Label",
            title=f"PCA — {info_retained:.2f}% Information Retained",
            labels={"Label": "Class"}
        )

    else:
        fig = px.scatter_3d(
            data,
            x="PC1",
            y="PC2",
            z="PC3",
            color="Label",
            title=f"PCA — {info_retained:.2f}% Information Retained",
            labels={"Label": "Class"}
        )

    fig.show()