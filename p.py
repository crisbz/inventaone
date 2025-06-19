import asyncio
import websockets
import json
import requests
import time

class BTCCLPStreamer:
    def __init__(self):
        self.usd_to_clp = None
        self.last_fx_update = 0

    async def actualizar_tipo_cambio(self):
        try:
            response = requests.get("https://open.er-api.com/v6/latest/USD")
            data = response.json()
            if data['result'] == 'success' and 'rates' in data and 'CLP' in data['rates']:
                self.usd_to_clp = data['rates']['CLP']
                self.last_fx_update = time.time()
                print(f"Tipo de cambio USD->CLP actualizado: {self.usd_to_clp}")
            else:
                print("Error: No se encontró tasa de cambio CLP.")
        except Exception as e:
            print("Error al obtener tipo de cambio:", e)

    async def stream_precio_btc(self):
        url = "wss://stream.binance.com:9443/ws/btcusdt@ticker"
        async with websockets.connect(url) as ws:
            print("Conectado a Binance WebSocket. Recibiendo precios BTC/USDT en tiempo real...")
            while True:
                # Actualizar tipo de cambio cada 600 segundos (10 minutos)
                if self.usd_to_clp is None or (time.time() - self.last_fx_update) > 600:
                    await self.actualizar_tipo_cambio()

                data = await ws.recv()
                json_data = json.loads(data)
                precio_usdt = float(json_data['c'])  # Precio de cierre actual

                if self.usd_to_clp:
                    precio_clp = precio_usdt * self.usd_to_clp
                    print(f"Precio BTC/USDT: ${precio_usdt:.2f} USD | Precio BTC/CLP: ${precio_clp:,.0f} CLP")
                else:
                    print(f"Precio BTC/USDT: ${precio_usdt:.2f} USD | Precio BTC/CLP: calculando...")

async def main():
    streamer = BTCCLPStreamer()
    await streamer.stream_precio_btc()

if __name__ == "__main__":
    asyncio.run(main())
