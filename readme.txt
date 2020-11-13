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

- Para usar la app:

El endpoint search_address de la app sirve para realizar consultas puntuales, posee 3 variables para la consulta y tiene la siguiente forma

{street: Calle a buscar,
 loc: localidad de la calle,
 dep: departamento de la calle}

Ejemplo: Para buscar la direccion MALDONADO 1420, MONTEVIDEO, MONTEVIDEO la url de consulta tiene la siguiente forma:

http://localhost:8000/search_address?street=maldonado%201420&loc=montevideo&dep=montevideo  

la respuesta de la app a esa consulta es la siguiente:
{"data": {"calleNormalizada": "MALDONADO", "idCalleIDE": 8795, "nro_puerta_aprox": 1421, "codigoPostal": 11200, "puntoX": -56.1847162255739, "puntoY": -34.90909689454292, "idPuntoIDE": 407875, "error": ""}}

Como ven, la APP aporta el nombre de la calle Normalizada, el Nº de identificación para la IDE, el número de puerta aproximado, el código postal, la latitud y longitud, y el Nº de identificacion del punto para la IDE.
En caso de error la APP devolverá todos los campos vacios y la especificación del error en la variable "errro".

El endpoint search_addresses_by_batch recibe un archivo txt donde cada línea corresponde a una dirección. 
Luego del proceso la app devuelve un archivo "result.txt", donde cada línea corresponde a la respuesta puntual a su correspondiente línea del archivo de consulta ingresado.