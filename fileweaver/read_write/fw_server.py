#### The websocket code is adapted from https://github.com/IRLL/HIPPO_Gym/
#### Implements the Pipeline pattern from ZMQ for the TCP Socket https://zeromq.org/socket-api/#pipeline-pattern
import asyncio, websockets, json
import zmq.asyncio
import zmq

from fileweaver.read_write.map_incoming_messages import (
    map_incoming_message_from_websocket,
)


class FWServer:
    def __init__(self, address="localhost", wsport=4000, tcpport=5555):
        self.start_server = websockets.serve(self.handler, address, wsport)
        context = zmq.asyncio.Context()
        self.tcpsocket = context.socket(zmq.PULL)
        self.tcpsocket.bind(f"tcp://*:{tcpport}")

    def start(self):
        """start

        Start the server
        """
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()

    async def handler(self, websocket, path):

        await self.register(websocket)

        consumerTask = asyncio.ensure_future(
            self.consumer_handler(websocket, self.tcpsocket)
        )
        producerTask = asyncio.ensure_future(
            self.producer_handler(websocket, self.tcpsocket)
        )
        done, pending = await asyncio.wait(
            [consumerTask, producerTask], return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        await websocket.close()
        return

    async def register(self, websocket):
        """register

        Keep track of clients.

        """
        self.user = websocket
        print("new task connected: {}".format(str(websocket)))

    async def consumer_handler(self, websocket, tcpsocket):
        """When messages from websocket are received, map them to the fileweaver command"""
        async for message in websocket:
            print("received message {}".format(message))
            # await tcpsocket.send_string(message)
            map_incoming_message_from_websocket(message)

    async def producer_handler(self, websocket, tcpsocket):
        """
        Look for messages to send to the websocket from the FW app (messages incoming via tcpsocket)
        asyncio.sleep() is required to make this non-blocking
        default sleep time is (0.01) which creates a maximum framerate of
        just under 100 frames/s. For faster framerates decrease sleep time
        however be aware that this will affect the ability of the
        consumer_handler function to keep up with messages from the websocket
        and may cause poor performance if the web-client is sending a high volume of messages.
        """

        while True:
            await self.producer(websocket, tcpsocket)
            await asyncio.sleep(0.01)

    async def producer(self, websocket, tcpsocket):
        """check tcpsocket and forward to websocket"""
        try:
            msg = await tcpsocket.recv_string()
            await websocket.send(json.dumps(msg))
        except UnicodeDecodeError:  # not needed ?
            msg = await tcpsocket.recv()
            print(msg)


if __name__ == "__main__":
    server = FWServer()
    server.start()
