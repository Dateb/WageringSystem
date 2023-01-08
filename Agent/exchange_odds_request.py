import json

import websocket
import _thread
import time
import rel
from websocket import ABNF


def on_message(ws: websocket.WebSocketApp, message):
    print(message)
    if message == "o":
        request = '["{\\"eventId\\":\\"32009630\\",\\"marketId\\":\\"1.208383769\\",\\"applicationType\\":\\"WEB\\"}"]'
        ws.send(request)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    pass

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://exch.piwi247.com/customer/ws/market-prices/223/hsosmrv2/websocket",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                            )
    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
