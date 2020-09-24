import pandas as pd
from difflib import SequenceMatcher, get_close_matches
import json
from urllib import parse , request
import ast # Para evaluar la string como diccionarios
from datetime import datetime
import numpy as np
import time
from IPython.display import HTML, display
import tabulate
import re



def process_street(street):
    forbidden_char = ["Nº", "S/N",",","."] #Remplaza caracteres que estorban en la busqueda
    non_street = [999] #Codigos para marcar que no es una calle
    special_streets = ["SENDA","CALLE"]
    
    
    if street in non_street: 
        return "",""
    
    try:
        street = street.upper() # Se fija si la calle contiene texto, Si es la calle es un numero lo devuelve como string
    except: 
        return str(street) , "" #LA API de IDE acepta las calles con numero en formato str(numero)   str(numero) 
    
    for char in forbidden_char:
        street = street.replace(char,"")
    try:
        if not street.split()[-2] in special_streets: #Para ver si el antepenultima palabra no es numero, para que no parsee ej "Senda 8"
            number = int(street.split()[-1])
            street = ' '.join(street.split()[:-1])
        else:
            number = ""
    except Exception as e:
        number = ""
    return street, number

def sugerir_calles(string,tryouts=3):
    """Sugiere calles a partir de una string"""
    query_args = {
        "entrada" : string, # La sugerencia a buscar
        "todos":False
    }
    root = 'https://direcciones.ide.uy/'
    URL = root + '/api/v0/geocode/SugerenciaCalleCompleta?'
    #r = request.Request(
    #        url=URL,
    #        data=parse.urlencode(query_args).encode('utf-8'),
    #    )
    
    while tryouts>0:
        try:
            r = request.urlopen(URL+parse.urlencode(query_args))
            data = r.read().decode('utf-8').replace('null','None')
            break
        except Exception as e:
            tryouts -= 1
            if tryouts == 0:
                print(e)
                return []
            time.sleep(0.5)
            
            
    if data=='[]':
        
        #print('No existe calle similar')
        return []
    else:
        return ast.literal_eval(data)

def sugerir_localidad(localidad,departamento,limit=10,tryouts=3):
    """Sugiere una localidad a partir de una string y checkea contra un departamento devolviendo sugerencia e id"""

    
    departamentos =(["artigas",
                    "canelones",
                    "cerro largo",
                    "colonia",
                    "durazno",
                    "flores",
                    "florida",
                    "lavalleja",
                    "maldonado",
                    "montevideo",
                    "paysandú",
                    "río negro",
                    "rivera",
                    "rocha",
                    "salto",
                    "san josé",
                    "soriano",
                    "tacuarembó",
                    "treinta y tres"])
    
    candidato_departamento = get_close_matches(departamento.lower(),departamentos,n=limit,cutoff=0.6)[0] 
    
    string = localidad + ", "+candidato_departamento
    query_args = {
        "limit": 10,
        "q" : string, # La sugerencia a buscar
        "soloLocalidad":True
    }
    
    
    root = 'https://direcciones.ide.uy/'
    URL = root + 'api/v1/geocode/candidates?'
    while tryouts>0:
        #r = request.Request(
        #        url=URL,
        #        data=parse.urlencode(query_args).encode('utf-8'),
        #    )
        try:
            r = request.urlopen(URL+parse.urlencode(query_args))
            break
        except Exception as e:
            tryouts -= 1
            if tryouts ==0:
                print(e)
                return {}
            time.sleep(0.5)
    
    data = r.read().decode('utf-8')
    
    if data=='[]':
        #print('No existe localidad similar')
        return {}
    else:
        data = ast.literal_eval(data.replace('null','None')) 
    try:
        localidades = [x.get('address').lower().split(',')[0] for x in data]
        idlocalidades = [x.get('idLocalidad') for x in data]
        loc_suggested = get_close_matches(localidad.lower(),localidades,n=limit,cutoff=0.6)[0] #Para localidad el matcheo queda en 0.6
        idloc_suggested = idlocalidades[localidades.index(loc_suggested)]
        return [loc_suggested , idloc_suggested]
    except Exception as e:
        #print("Este erro",e)
        loc_suggested = " "
        idloc_suggested = " "
        return [loc_suggested , idloc_suggested]

def search_from_API(street,loc,dep,warning=False):  #Mejorar la funcion si no tiene localidad
    """Encuentra una localidad dada una calle sugerida y una localidad. Devuelve un diccionario con los datos de esa calle"""
    street, number = process_street(street)
    if street.isdigit():
        street += " " + street # La API busca los numeros de esta forma, ej: "60 60" es una busqueda valida para la calle 60
    suggestions = sugerir_calles(street)  #Consulta por calles similares a la API IDE
    try:
        street = str(street) #Transformo las calles de numeros en strings #transformo las 
    except Exception as e:
        return {}
    street = street.strip()   #Quito los espacios en blanco
    dep = dep.strip()
    if not suggestions: #Si no se devuelven calles similares
        if warning:
            print('No se encuentra calle simular')
        return  {}
    streets = [x.get('calle').lower() for x in suggestions] # Hay que trabajar con lower dado que las mayusculas afectan el ratio
    
    suggested_loc = [x.get('localidad').lower() for x in suggestions if x.get('localidad') is not None]
    suggested_idstreet = [x.get('idCalle') for x in suggestions] 
    suggested_idloc = [x.get('idLocalidad') for x in suggestions if x.get('idLocalidad') is not None] 
    suggested_dep = [x.get('departamento').lower() for x in suggestions if x.get('departamento') is not None] 
    suggested_streets = get_close_matches(street.lower(),street,n=14,cutoff=0.6) 
    try:
        loc, idloc = sugerir_localidad(loc.lower(),dep)
    except:
        return {}
    if not loc:
        if warning:
            print("no se encuentra localidad")
        return {}
    
    suggested_street_indexes = [x for x in range(len(suggested_loc)) if suggested_loc[x] == loc]
    suggested_streets = [streets[x] for x in suggested_street_indexes]
    suggested_idstreet = [suggested_idstreet[x] for x in suggested_street_indexes]
    suggested_dep =  [suggested_dep[x] for x in suggested_street_indexes]
    suggested_idloc = [suggested_idloc[x] for x in suggested_street_indexes]
   
    
    if not suggested_streets:
        if warning:
            print('No se encuentra calle similar')
        return {}
    else:
        try:
            result = ({'calle':suggested_streets[0], #Solo se informa el primero
                       'numero': number,
                   'id':suggested_idstreet[0],
                   'localidad':loc,
                   'idlocalidad':idloc,
                   'departamento':suggested_dep[0],
                   'fuente':'API INE'})
            return result
        except Exception as e:
            print(e, "FINAL")
            return {}

def search_from_frame(street,loc,dep,df):
    "Hace una busqueda en en cascada dep/loc/calle devolviendo un diccionario de datos"
    dep = dep.upper() #Pasa a mayusculas ya que esta asi en el DF 
    
    street, number = process_street(street)
    try:
        suggested_dep = get_close_matches(dep,df.departamento.unique(),n=14,cutoff=0.6)[0] #Prueba buscar el departamento
    except: # No se encuentra departamento
        return {}
    try:
        suggested_loc = get_close_matches(loc,df[df['departamento']==suggested_dep]['localidad'].unique(),n=14,cutoff=0.6)[0]
        
    except Exception as e:
        #print("No encuentro la localidad")
        return {} #No se encuentra la localidad
    try:
        suggested_street = get_close_matches(street,df[(df['departamento']==suggested_dep)&(df['localidad']==suggested_loc)]['calle'].unique(),n=10,cutoff=0.6)[0]
    except Exception as e:
        try: #Si la distancia de edición no funciona cuento cuantas veces aparecen los nombres de las palabras dentro de la calle en los candidatos. Quien tiene más palabras gana
            candidates = df[(df['departamento']==suggested_dep)&(df['localidad']==suggested_loc)]['calle'].unique()
            word_counts = [count_matches(street,candidate) for candidate in candidates]
            suggested_street = candidates[np.argmax(word_counts)]
        except:
            return {}
        
    try:
        _ , idloc = sugerir_localidad(suggested_loc,suggested_dep,limit=10)
        result = ({'calle':suggested_street , #Solo se informa el primero
                   'numero': number,
                   'id': int(df[(df['departamento']==suggested_dep)&(df['calle']==suggested_street)&(df['localidad']==suggested_loc)]['idcalle']),
                   'localidad':suggested_loc,
                   'idlocalidad':idloc,
                   'departamento':suggested_dep,
                   'fuente':'Codificador'})
        return result
    except:
        return {}


def search_street(street,loc,dep,df):
    special_charecters = [",","-"]
    possible_locs = []
    for char in special_charecters: #Search for only one of this characters. 
        if char in loc:
            possible_locs = loc.split(char)
            break
    
    if isinstance(loc,str) :
        possible_locs.append(loc)
    else:
        possible_locs = [x.strip().upper() for x in possible_locs]
        
    if not dep:
        for loc in possible_locs:
            dep = suggest_dep(loc)
            if dep:
                possible_locs.pop(possible_locs.index(loc))
                break
         
    for loc in possible_locs:
        result = search_from_API(street,dep,loc)
        if result:
            return result
        else:
            result = search_from_frame(street,loc,dep,df)
            if result:
                return result  
            # Continua al proximo juego de palabras de la lista
    return {} # Si no encuentra match devuelve vacio


def suggest_dep(string):
    """Suggest a departamento """
    departamentos =(["artigas",
                    "canelones",
                    "cerro largo",
                    "colonia",
                    "durazno",
                    "flores",
                    "florida",
                    "lavalleja",
                    "maldonado",
                    "montevideo",
                    "paysandú",
                    "río negro",
                    "rivera",
                    "rocha",
                    "salto",
                    "san josé",
                    "soriano",
                    "tacuarembó",
                    "treinta y tres"])
    return get_close_matches(string.lower(),departamentos,n=2,cutoff=0.6)[0]


def check_results_from_dataframe(columna_calle,columna_localidad,columna_departamento,frame,referencia):
    "Analiza un frame para buscar calles"
    dep_error = []
    loc_error = []
    calle_error = []
    start = datetime.now()
    start_index = ""
    df_append = pd.DataFrame()
    for index, row in frame.iterrows():
        if not start_index:
            start_index = index
        if index%1000 == 0:
            #d = {'calle':calle_error, 'localidad':loc_error,'departamento':dep_error}
            #inter = pd.DataFrame(data = d)
            #df_append.append(inter)
            print("Van {} y faltan {}, van {} errores".format(index,frame.shape[0]-index+start_index,len(dep_error)))
            #print("Van {} minutos".format((datetime.now() - start).seconds/60))
        calle = row[columna_calle]
        localidad =  row[columna_localidad].strip()
        departamento = row[columna_departamento].strip()
        
        result = search_street(calle,localidad,departamento,referencia)
        if not result:
            dep_error.append(departamento)
            loc_error.append(localidad)
            calle_error.append(calle)
    d = {'calle':calle_error, 'localidad':loc_error,'departamento':dep_error}
    inter = pd.DataFrame(data = d)
    df_append = df_append.append(inter)
    return df_append


