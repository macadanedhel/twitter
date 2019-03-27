# Twitter

Learn some new concepts, testing and playing

## Getting Started

Obtener datos de twitter. Primero descargar los usuarios que se sigue y los que te siguen.

### 1. Ver las tendencias

| opcion | abreviatura | descripción |
|:------:|:-----------:|-------------|
| t | trends | Ver las tendencias |
|ta | trendAvailable | Paises hablando WOEID |
|p| print | imprime a fichero |
|db|mongodb|  a un mongodb|

### 2. Amiguete amiguete

| opcion | abreviatura | descripción |
|:------:|:-----------:|-------------|
|fr | friends | siguiendo |
|rf | other_friend SCREEN_NAME | los que sigue SCREEN_NAME |
|fo| followers | los que siguen a la cuenta |
|of| other_follower SCREEN_NAME | los que siguen a SCREEN_NAME |
|m| memberships | Listas en las que está apuntado  |
|l| lists SCREEN_NAME | listas de un usuario me o SCREEN_NAME |
|p| print | imprime a fichero |
|db|mongodb|  a un mongodb|

### 3. Tweets

| opcion | abreviatura | descripción |
|:------:|:-----------:|-------------|
| w | tweets | tweets de la cuenta |
| u | tweets_user SCREEN_NAME | tweets de SCREEN_NAME |
|p| print | imprime a fichero |
|db|mongodb|  a un mongodb|

### 4. Gestión de IDs, names y screen_names

| opcion | abreviatura | descripción |
|:------:|:-----------:|-------------|
| n | get_userid NAME| Obtiene el userId a partir del name o screen_name  |
| nr | get_userid_regex STRING | Obtiene el userId a partir del name o screen_name basado en regex |
| gn | get_username userID| Obtiene el name y screen_name a partir de userID |
| r | users userID| Obtiene el name y screen_name a partir de userID |
|ut| userstweets | usersid, numero de tweets ordenado descendente | 
|a| resolve_na | resuelve el userid a name y screen_name | 

### 5. Datos para ir jugando
Estos datos salen de la mongodb

| opcion | abreviatura | descripción |
|:------:|:-----------:|-------------|
| u2csv | user2csv | Saca los datos a un csv para empezar a jugar |
| d2neo | data2neo | Datos para importar en neo4j, usuarios, friends, followers |
|gtu| get_tweet_user NAME | devuelve los tweets por name o screen_name|
|p| print | imprime a fichero |
 
### 6. Busquedas de palabras, hashtags y usuarios
Estos datos salen de la mongodb
 
| opcion | abreviatura | descripción |
|:------:|:-----------:|-------------|
| hh | hide | Oculta la salida de get_tweet_user2analyze |
| gtua | get_tweet_user2analyze | Busca en los tweets bajados por name o screen_name las palabras, hashtag y usuarios |
| au | user | Muestra usuarios en la búsqueda get_tweet_user2analyze |
| ah | hash | Muestra los hashtag en la búsqueda get_tweet_user2analyze |
| aw | words | Muestra las palabras en la búsqueda get_tweet_user2analyze |
| txu | tweetsxuser | Muestra los ids ordenados por los tweets obtenidos |
| tt | top | Muestra el top 10 de los valores encontrados | 
 


### Variables

#### path
los directorios
``` 
[path]
config : config
data : data
```
#### prefijos
Para construir los ficheros
``` 
[prefix]
trends: trends
trendsavailable: trends_available
friends: friends
followers: followers
tweets: tweets
user2csv: user2csv
``` 
#### mongodb
la conexión al mongo y las colecciones
``` 
[mongodb]
ip:192.168.1.1
port:27017
friends:friends
followers:followers
``` 
#### neo4j
Conexión, autenticación, rutas de importación y claves
``` 
[neo4j]
ip:192.168.99.100
bolt:17687
http:17474
https:17473
user: neo4j
password: neo4j
``` 
Rutas de importación. Esto lo hago en docker, la ruta datapath tiene que montarse en el docker.
El neo4j debe permitir cargar de esa ruta.
``` 
#---------------------------------
datapath=/Users/e019553/Documents/Kitematic/neo4j_mac/import
# change conf to /data/import
remotepath=/
#---------------------------------
userfile:user
user_key:verified,screen_name,default_profile,name
lang:lang
lang_key:lang,
location: location
location_key:time_zone,utc_offset,location
followers:followers
followers_key:friend,user
friends:friends
friends_key:user,friend
``` 
#### mas o menos
* Selecciona una cuenta y mira si mola, `pwt.v.1.py -r nombre_cuenta` si mola -db
* Escoge un usuario y obten tweets, `pwt.v.1.py -u nombre_cuenta -db`
* Escoge un usuario y obten a los que sigue  `pwt.v.1.py -rf nombre_cuenta -db`
* Escoge un usuario y obten los que le siguen  `pwt.v.1.py -of nombre_cuenta -db`, esto puede ser de poco valor
* Escoge un usuario y mira a ver que le interesa, words, hashtag y usuarios, `pwt.v.1.py -gtua nombre_cuenta` para ver el top 10 `tt` y si solo se quiere eso `hh`. Adminte modificadores por concepto



#### Prerequisites

Leete el requeriments.txt
```
:-D
```

### Installing

## Acknowledgments

* [Matthew A. Russell](https://github.com/ptwobrussell) for [Mining the Social Web](https://www.amazon.com/gp/product/1449388345?tag=oreonbl-20)
* [Vicente Aguilera Diaz](https://github.com/vaguileradiaz/tinfoleak) a good tool