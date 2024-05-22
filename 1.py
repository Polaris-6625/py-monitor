import asyncio
import websockets
import psutil
import time
import json

async def send_network_stats_to_clients(websocket_set, interface, interval=1):
    old_sent, old_recv = get_network_stats(interface)
    if old_sent is None or old_recv is None:
        return

    print(f"Monitoring network traffic on interface '{interface}' (Press Ctrl+C to stop)")
    print("Time         Sent (kB)     Received (kB)")

    try:
        while True:
            await asyncio.sleep(interval)
            new_sent, new_recv = get_network_stats(interface)

            sent = (new_sent - old_sent) / 1024
            recv = (new_recv - old_recv) / 1024

            timestamp = time.strftime("%H:%M:%S")
            print(f"{timestamp}\t{sent:10.2f}\t{recv:10.2f}")

            # Send the stats to all connected clients
            for ws in websocket_set:
                await ws.send(
                    json.dumps(
                        {"timestamp": timestamp, "sent": sent, "received": recv}
                    )
                )

            old_sent, old_recv = new_sent, new_recv

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

async def echo(websocket, path):
    # Add the new client to the set of connected clients
    websocket_set.add(websocket)
    try:
        async for message in websocket:
            pass  # You can handle incoming messages here if needed
    finally:
        # Remove the client from the set when it disconnects
        websocket_set.remove(websocket)

async def start_websocket_server(interface, port):
    global websocket_set
    websocket_set = set()
    
    async with websockets.serve(echo, "localhost", port):
        await send_network_stats_to_clients(websocket_set, interface)

def get_network_stats(interface):
    net_io_counters = psutil.net_io_counters(pernic=True)
    if interface not in net_io_counters:
        print(f"Interface '{interface}' not found.")
        print("Available interfaces:")
        for key in net_io_counters.keys():
            print(f"- {key}")
        return None, None

    stats = net_io_counters[interface]
    return stats.bytes_sent, stats.bytes_recv

if __name__ == "__main__":
    interface = "en0"  # Replace with the desired network interface name
    port = 8765  # WebSocket server port
    
    # Start the WebSocket server and network monitoring
    asyncio.run(start_websocket_server(interface, port))