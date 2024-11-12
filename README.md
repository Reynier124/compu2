# compu2
### TP2 guia de uso
1) Crear un entorno virtual con las librerias de requirements utilizando el "pip install -r requirements"
2) Iniciar el servidor llamado "process_server". Tener en cuenta que si quires usar argparse no usar las opciones de escuchar todas las interfaces porque utilizan ambas IP el mismo puerto
3) Iniciar el servidor llamado "client_server"
4) Paa comunicarse con el servidor HTTP hace falta un post en "/process_image" y debes mandar un string con el siguiente json: {"path": "path de la imagen que quieres modifcar", "scale":"número flotante mayor a 0 para escalar la imagen", "name": "nombre de la imagen resultante (Debe tener el formato de la imagen, es decir, si esta en png, jpg o otro formato), "path_result":"donde quieres que se guarde la imagen"}
