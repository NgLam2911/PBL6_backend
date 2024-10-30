# Handle base command from CLI

from queue import Queue
import threading

cmd_queue = Queue()
stop_event = threading.Event()

def command_thread():
    while not stop_event.is_set():
        try:
            command = input()
            cmd_queue.put(command)
        except EOFError:
            break
        
def command_handler():
    while not stop_event.is_set():
        cmd = cmd_queue.get()
        onCommand(cmd)

def onCommand(cmd):
    match cmd:
        case "kill":
            print("Killing server...")
            stop_event.set()
        case "help":
            print("Available commands:")
            print("kill - Kill the server")
            print("help - Show this message")
        case None:
            pass
        case _:
            print("Unknown command. Type 'help' for a list of commands.")