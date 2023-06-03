from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from datetime import datetime
from fastapi.security import HTTPBearer
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional, List

from jwt_config import dame_token, valida_token
from config.base_datos import sesion, motor, base
from modelos.ventas import Ventas as VentasModelo


app = FastAPI()
app.title = 'Aplicacion de Ventas'
app.version = '1.0.1'

base.metadata.create_all(bind=motor)


#modelos
class Usuario(BaseModel):
    email:str
    clave:str 


class Ventas(BaseModel):
    id: Optional[int] = None
    fecha: str
    tienda: str = Field(min_length=4, max_length=10)
    importe: int

    class Config:
        schema_extra = {
            'example':{
                'fecha':datetime.now(),
                'tienda':'Tienda 01',
                'importe':1500
            }
        }


#PORTADOR TOKEN
class Portador(HTTPBearer):
    async def __call__(self, request:Request):
        autorizacion = await super().__call__(request)
        dato = valida_token(autorizacion.credentials)

        if dato['email'] != 'kuky@lanegra.cl':
            raise HTTPException(status_code=403, detail='No Autorizado')


#INICIO
@app.get('/', tags=['Inicio'])
def mensaje():
    return HTMLResponse('<h2>Titulo HTML desde FastApi</h2>')


#TODAS LAS VENTAS
@app.get('/ventas', tags=['Ventas'], response_model=List[Ventas], status_code=200, dependencies=[Depends(Portador())])
def dame_ventas() -> List[Ventas]:

    db = sesion()
    resultado = db.query(VentasModelo).all()

    return JSONResponse(content=jsonable_encoder(resultado), status_code=200)


#VENTAS POR ID
@app.get('/ventas/{id}', tags=['Ventas'], response_model=Ventas, status_code=200)
def dame_ventas_id(id:int = Path(ge=1, le=1000)) -> Ventas:

    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(content={'mensaje':'No se encontro ventas con ese ID'}, status_code=404)

    return JSONResponse(content=jsonable_encoder(resultado), status_code=200)


#VENTAS POR TIENDA
@app.get('/ventas/', tags=['Ventas'], response_model=List[Ventas], status_code=200)
def dame_ventas_tienda(tienda:str = Query(min_length=4, max_length=20)) -> List[Ventas]:

    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.tienda == tienda).all()

    if not resultado:
        return JSONResponse(content={'mensaje':'No se encontro esa tienda'}, status_code=404)

    return JSONResponse(content=jsonable_encoder(resultado), status_code=200)


#AGREGAR UNA VENTA
@app.post('/ventas', tags=['Ventas'], response_model=dict, status_code=201)
def crea_venta(venta: Ventas) -> dict:

    db = sesion()
    nueva_venta = VentasModelo(**venta.dict())
    db.add(nueva_venta)
    db.commit()

    return JSONResponse(content={'mensaje':'Venta Registrada'}, status_code=201)


#ACTUALIZAR VENTA
@app.put('/ventas/{id}', tags=['Ventas'], response_model=dict, status_code=200)
def actualiza_ventas(id:int, venta:Ventas) -> dict:

    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()

    if not resultado:
        return JSONResponse(content={'mensaje':'No se encontro la venta con ese ID'}, status_code=404)
    
    resultado.fecha = venta.fecha
    resultado.tienda = venta.tienda
    resultado.importe = venta.importe
    db.commit()

    for ele in ventas:
        if ele['id'] == id:
            ele['fecha'] = venta.fecha
            ele['tienda'] = venta.tienda
            ele['importe'] = venta.importe
    return JSONResponse(content={'mensaje':'Venta Actualizada'}, status_code=200)


#ELIMINAR VENTA
@app.delete('/ventas/{id}', tags=['Ventas'], response_model=dict, status_code=200)
def borrar_ventas(id:int) -> dict:

    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()

    if not resultado:
        return JSONResponse(content={'mensaje':'No se encontro la venta con ese ID'}, status_code=404)

    db.delete(resultado)
    db.commit()

    return JSONResponse(content={'mensaje':'Venta Eliminada'}, status_code=200)


#RUTA PARA EL LOGIN
@app.post('/login', tags=['Autenticacion'])
def login(usuario:Usuario):
    if usuario.email == 'kuky@lanegra.cl' and usuario.clave == '123456':
        #OBTENEMOS TOKEN
        token:str = dame_token(usuario.dict())
        return JSONResponse(status_code=200, content=token)
    else:
        return JSONResponse(content={'mensaje':'Acceso Denegado'}, status_code=404)