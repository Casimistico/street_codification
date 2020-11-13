Para instalar la app:

- En una maquina virtual instalar python, luego instalar los paquetes necesarios en requirements.txt.
en bash o cmd >>> pip install requirements.txt

- Para inicializar la aplicación comandar en bash o cmd hug -f app.py

La API está hecha con el paquete hug. La documentación se encuentra disponible en http://www.hug.rest/


En el archivo "Consideraciones particulares.xlsx" los usuarios pueden agregar información relativa:

- Sinonimos de calles "sin nombre" (Ej, S-N, S/N)

- Sinonimos de apartamento (Ej, apto), necesarias para que la app de una correcta dirección. 

- Caracteres prohibidos que aparecen a la hora de ingresar datos que impiden el rendimiento de la app. 

- Vialidades que pueden contener un número en su nombre (ej calle, senda). Esto sirve para poder codificar correctamente direcciones de la forma "Calle 2 Nº 24"

