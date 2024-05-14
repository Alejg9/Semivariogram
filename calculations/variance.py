import numpy as np
import xarray as xr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


# Creamos la clase grid, que se encarga de manejar los datos del grid
class Grid:
    # Inicializamos la clase con el tamaño del grid
    def __init__(self, x_size, y_size):

        # Creamos un grid de ceros con las dimensiones especificadas
        x_size = int(x_size)
        y_size = int(y_size)

        x = np.linspace(0, x_size - 1, x_size)
        y = np.linspace(0, y_size - 1, y_size)

        grid = np.zeros((x_size, y_size))

        # Sustituimos los ceros por valores nan
        grid[grid == 0] = np.nan

        # Creamos un array con coordenadas x y y
        grid = xr.DataArray(grid, coords=[y, x], dims=["y", "x"])

        # Inicializamos las variables de la clase

        self.grid = grid
        self.lag = None
        self.lags = None
        self.theta = None
        self.az = None
        self.wb = None

    # Método que se encarga de añadir los datos al grid
    def addData(self, x, y, data):
        # Accedemos al grid
        grid = self.grid

        # Medimos los datos y añadimos los valores al grid
        for i in range(len(data)):
            grid[y[i]][x[i]] = data[i]

        # Actualizamos el grid
        self.grid = grid

    # Método que se encarga de dibujar el cono
    def drawCone(self, lag, lags, wb, az, theta):
        # Accedemos al grid
        grid = self.grid

        # Convertimos los valores a float
        az = float(az)
        theta = float(theta)
        wb = float(wb)
        lag = float(lag)
        lags = int(lags)

        # Convertimos los ángulos a radianes
        az = np.radians(az)
        theta = np.radians(theta)

        # Guardamos los valores en las variables de la clase
        self.lag = lag
        self.lags = lags
        self.theta = theta
        self.az = az
        self.wb = wb

        # Accedemos a los valores del grid
        data = grid.values

        distances = []
        x = []
        y = []
        data_values = []

        # Inicializamos las coordenadas del punto inicial
        x0 = 0
        y0 = 0

        # Verificamos si hay valores en el grid
        control = grid.sum(dim="x").sum(dim="y").values

        if control > 0:
            # Si hay valores recorremos los valores del grid para calcular las distancias al origen de cada punto
            for i in range(len(data)):
                for j in range(len(data[0])):
                    if data[i][j] > 0:
                        r = np.sqrt((j - x0) ** 2 + (i - y0) ** 2)
                        distances.append(r)
                        x.append(j)
                        y.append(i)
                        data_values.append(data[i][j])

            distances = np.array(distances)
            x = np.array(x)
            y = np.array(y)
            data_values = np.array(data_values)

            x = x[np.argsort(distances)]
            y = y[np.argsort(distances)]
            distances = distances[np.argsort(distances)]

            x0 = x[0]
            y0 = y[0]

        # Largo total del cono
        L = lag * (lags + 1)
        L = np.arange(0, L, L - 1)

        hcone = wb / np.tan(theta)

        # Lineas del angulo de tolerancia

        L2 = np.sqrt(hcone**2 + wb**2)
        L2 = np.arange(0, L2, L2 - 1)

        # Puntos de las lineas de tolerancia

        yt2 = L2 * np.cos(az + theta) + y0
        xt2 = L2 * np.sin(az + theta) + x0

        yt3 = L2 * np.cos(az - theta) + y0
        xt3 = L2 * np.sin(az - theta) + x0

        # Distancia de las lineas laterales

        l = L[-1] - hcone

        l = np.arange(0, l, l - 1)

        # Puntos de las lineas laterales

        yl2 = l * np.cos(az) + yt2[-1]
        xl2 = l * np.sin(az) + xt2[-1]

        yl3 = l * np.cos(az) + yt3[-1]
        xl3 = l * np.sin(az) + xt3[-1]

        # Puntos del borde del cono

        xb = [xl2[-1], xl3[-1]]
        yb = [yl2[-1], yl3[-1]]

        # Tolerancia de los lags

        Lt = []

        for i in range(len(L)):
            if i < len(L) - 1:
                Lt.append(L[i] + lag / 2)

        Lt = np.array(Lt)

        xr = Lt * np.sin(az) + x0
        yr = Lt * np.cos(az) + y0

        # Creamos el gráfico

        fig = make_subplots(specs=[[{"secondary_y": False}]])

        values = grid.values.copy()

        values[values > 0] = 1

        fig.add_trace(
            go.Heatmap(z=grid.values, x=grid.x, y=grid.y, showscale=False)
        )

        fig.add_trace(
            go.Scatter(
                mode="lines",
                x=xr,
                y=yr,
                showlegend=False,
                line=dict(color="black", width=1),
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                mode="lines",
                x=xt2,
                y=yt2,
                showlegend=False,
                line=dict(color="black", width=1),
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                mode="lines",
                x=xt3,
                y=yt3,
                showlegend=False,
                line=dict(color="black", width=1),
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                mode="lines",
                x=xl2,
                y=yl2,
                showlegend=False,
                line=dict(color="black", width=1),
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                mode="lines",
                x=xl3,
                y=yl3,
                showlegend=False,
                line=dict(color="black", width=1),
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                mode="lines",
                x=xb,
                y=yb,
                showlegend=False,
                line=dict(color="black", width=1),
            ),
            secondary_y=False,
        )

        fig.update_layout(autosize=False, width=500, height=500, title="Grid de puntos + Cono", xaxis_title="X", yaxis_title="Y")

        return fig

    # Método que se encarga de calcular y dibujar el variograma
    def drawVariogram(self):
        # Accedemos a las variables de la clase
        grid = self.grid
        lag = self.lag
        lags = self.lags
        theta = self.theta
        az = self.az
        wb = self.wb
        # Drop nan values
        data = grid.values

        distances = []
        x = []
        y = []
        data_values = []

        x0 = 0
        y0 = 0
        # Recorre los valores del grid para calcular las distancias al origen de cada punto
        for i in range(len(data)):
            for j in range(len(data[0])):
                if data[i][j] > 0:
                    r = np.sqrt((j - x0) ** 2 + (i - y0) ** 2)
                    distances.append(r)
                    x.append(j)
                    y.append(i)
                    data_values.append(data[i][j])

        distances = np.array(distances)
        x = np.array(x)
        y = np.array(y)
        data_values = np.array(data_values)

        # Ordena los valores, coordenadas y distancias por distancia
        x = x[np.argsort(distances)]
        y = y[np.argsort(distances)]
        data_values = data_values[np.argsort(distances)]
        distances = distances[np.argsort(distances)]

        # Inicializa el calculo de la varianza para cada punto
        
        semivariance = np.zeros(lags)
        pairs = np.zeros(lags)

        for i in range(len(x)):
            x = x.astype(float)
            y = y.astype(float)
            x0 = x[i]
            y0 = y[i]

            # Largo total del cono
            L = lag * (lags + 1)
            L = np.arange(0, L, L - 1)

            hcone = wb / np.tan(theta)

            # Lineas del angulo de tolerancia

            L2 = np.sqrt(hcone**2 + wb**2)
            L2 = np.arange(0, L2, L2 - 1)

            # Puntos de las lineas de tolerancia

            yt2 = L2 * np.cos(az + theta) + y0
            xt2 = L2 * np.sin(az + theta) + x0

            yt3 = L2 * np.cos(az - theta) + y0
            xt3 = L2 * np.sin(az - theta) + x0

            # Distancia de las lineas laterales

            l = L[-1] - hcone

            l = np.arange(0, l, l - 1)

            # Puntos de las lineas laterales

            yl2 = l * np.cos(az) + yt2[-1]
            xl2 = l * np.sin(az) + xt2[-1]

            yl3 = l * np.cos(az) + yt3[-1]
            xl3 = l * np.sin(az) + xt3[-1]

            # Tolerancia de los lags

            Lt = []

            for i in range(len(L)):
                if i < len(L) - 1:
                    Lt.append(L[i] + lag / 2)

            Lt = np.array(Lt)

            xr = x.copy()
            yr = y.copy()
            data_valuesr = data_values.copy()
            distancesr = distances.copy()

            # Define los puntos y líneas que forman la figura del cono

            cone_polygon = Polygon(
                [
                    (xt2[0], yt2[0]),
                    (xl2[0], yl2[0]),
                    (xl2[-1], yl2[-1]),
                    (xl3[-1], yl3[-1]),
                    (xl3[0], yl3[0]),
                    (xt3[0], yt3[0]),
                ]
            )

            # Recorremos los datos y verificamos si están dentro del cono, en caso de no estarlo eliminamos ese dato
            for i in range(len(x)):
                point = Point(x[i], y[i])
                if cone_polygon.contains_properly(point) or x[i] == x0 and y[i] == y0:
                    pass
                else:
                    data_valuesr[i] = np.nan
                    xr[i] = np.nan
                    yr[i] = np.nan
                    distancesr[i] = np.nan
            
            # Eliminamos valores nulos de nuestro array
            data_valuesr = data_valuesr[~np.isnan(data_valuesr)]
            xr = xr[~np.isnan(xr)]
            yr = yr[~np.isnan(yr)]
            distancesr = distancesr[~np.isnan(distancesr)]

            # Recorremos cada lag y acumulamos la suma de las diferencias al cuadrado de los datos
            for i in range(1, lags + 1):
                data_lag = []
                # Recorremos los datos y verificamos si están dentro del lag, en caso de no estarlo eliminamos ese dato
                for j in range(1,len(distancesr)):
                    if distances[j] > (lag / 2) and distances[j] <= lag * i:
                        data_lag.append(data_valuesr[j])

                result = 0
                # Calculamos la suma de la diferencia al cuadrado de los datos
                for k in range(len(data_lag)):
                    result = result + (data_lag[0] - data_lag[k]) ** 2
                    pairs[i - 1] += 1
                
                # Añadimos el resultado al array de semivarianza
                semivariance[i - 1] += result
        
        # Calculamos la semivarianza final
        semivariance = semivariance / (2 * pairs)

        # Creamos el gráfico
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=np.arange(0, lags * lag, lag), y=semivariance, mode="lines+markers"
            )
        )

        fig.update_layout(
            autosize=False, 
            width=500, 
            height=500, 
            title="Semivariograma", 
            xaxis_title="Distancia (m)", 
            yaxis_title="Semivarianza(h)")

        return fig