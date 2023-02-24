# FileSocket
Library for file transfer and remote PC control

## Links
- [Client GitHub](https://github.com/Qolorerr/FileSocketClient)
- [Server GitHub](https://github.com/Qolorerr/FileSocketServer) - Client needs it to establish connection to PC

## Quick usage
```python
from pathlib import Path
from filesocket import Storekeeper, ManagedClient, ManagingClient

store_keeper = Storekeeper()

# Create managed client
client = ManagedClient(store_keeper, port=7999, require_token='token')
client.run()

# Create managing client
client = ManagingClient(store_keeper, device_id='2', device_secure_token='token')
client.run(text_ui=False)

# Send cmd command
client.cmd_command('ipconfig')

# Send file
client.send_file(Path("path/to/file/to/send"), Path("path/where/to/put"))
```
