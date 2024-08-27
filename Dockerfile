# Usar la imagen base de Python 3.9
FROM python:3.9

# Crear un directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requisitos y el código fuente al contenedor
COPY requirements.txt ./
COPY . .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install "cloud-sql-python-connector[pymysql]"

# Exponer el puerto en el que la aplicación se ejecutará
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
