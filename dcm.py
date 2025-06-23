import marimo

__generated_with = "0.14.6"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    # 1. Librerías necesarias
    import numpy as np
    import pandas as pd
    from sklearn.cluster import SpectralClustering
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBRegressor
    from pulp import LpProblem, LpVariable, lpSum, LpMaximize
    import matplotlib.pyplot as plt

    # 2. Generación de datos sintéticos
    n_tiendas, n_categorias = 50, 5
    rnd = np.random.RandomState(0)
    ventas = rnd.poisson(lam=20, size=(n_tiendas, n_categorias))
    lat = rnd.uniform(-34.7, -34.5, n_tiendas)
    lon = rnd.uniform(-58.5, -58.3, n_tiendas)
    df = pd.DataFrame(ventas, columns=[f"cat_{i+1}" for i in range(n_categorias)])
    df["lat"], df["lon"] = lat, lon
    df["tienda_id"] = [f"T{i+1}" for i in range(n_tiendas)]

    # 3. Clustering de tiendas
    X = StandardScaler().fit_transform(df[[f"cat_{i+1}" for i in range(n_categorias)] + ["lat", "lon"]])
    df["cluster"] = SpectralClustering(n_clusters=4, affinity="nearest_neighbors", n_neighbors=10, random_state=1).fit_predict(X)

    # 4. Generación de datos históricos con promociones y clima
    dias_hist = 120
    data = []
    for dia in range(dias_hist):
        promo = int(dia % 30 < 7)  # 7 días de promoción cada 30
        temp = 15 + 10 * np.sin(2 * np.pi * dia / 365) + rnd.normal(scale=3)
        for _, row in df.iterrows():
            for c in range(n_categorias):
                base = row[f"cat_{c+1}"]
                ventas = max(0, base + 2*promo + 0.3 * temp + rnd.normal(scale=5))
                data.append({"cluster": row.cluster, "dia": dia, "cat": c, "promo": promo, "temp": temp, "ventas": ventas})
    df_hist = pd.DataFrame(data)

    # 5. Preparación de datos para XGBoost
    Xf = pd.get_dummies(df_hist[["dia", "cluster", "cat", "promo"]].astype(int), columns=["cluster", "cat", "promo"])
    Xf["temp"] = df_hist["temp"]
    y = df_hist["ventas"]
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(Xf, y, test_size=0.2, random_state=1)

    # 6. Entrenamiento del modelo XGBoost
    modelo = XGBRegressor(n_estimators=200, random_state=1)
    modelo.fit(X_train, y_train)

    # 7. Pronóstico para los próximos 7 días
    futuro = []
    for dia in range(dias_hist, dias_hist+7):
        promo = int(dia % 30 < 7)
        temp = 15 + 10 * np.sin(2 * np.pi * dia / 365)
        for cl in df.cluster.unique():
            for c in range(n_categorias):
                futuro.append({"dia": dia, "cluster": cl, "cat": c, "promo": promo, "temp": temp})
    df_futuro = pd.DataFrame(futuro)
    Xpf = pd.get_dummies(df_futuro[["dia", "cluster", "cat", "promo"]].astype(int), columns=["cluster", "cat", "promo"]).reindex(columns=Xf.columns, fill_value=0)
    Xpf["temp"] = df_futuro["temp"]
    df_futuro["pronostico"] = modelo.predict(Xpf)

    # 8. Optimización de surtido con restricciones reales
    margenes = np.linspace(1, 5, n_categorias)
    espacio = np.linspace(1, 3, n_categorias)
    K = 3  # Límite de SKUs
    espacio_max = 5
    resultados = []
    for cl in df.cluster.unique():
        df_cl = df_futuro[df_futuro.cluster == cl].groupby("cat")["pronostico"].sum()
        prob = LpProblem(f"asort_cl{cl}", LpMaximize)
        x = LpVariable.dicts("x", list(range(n_categorias)), cat="Binary")
        prob += lpSum(df_cl[c] * margenes[c] * x[c] for c in range(n_categorias))
        prob += lpSum(x.values()) <= K
        prob += lpSum(espacio[c] * x[c] for c in range(n_categorias)) <= espacio_max
        prob.solve()
        seleccion = [c+1 for c in range(n_categorias) if x[c].value() == 1]
        resultados.append({"cluster": cl, "seleccion": seleccion})
    df_resultados = pd.DataFrame(resultados)

    # 9. Visualización de resultados
    print("Pronóstico de ventas para los próximos 7 días:\n", df_futuro.head())
    print("\nSelección de surtido por clúster:\n", df_resultados)

    return


if __name__ == "__main__":
    app.run()
