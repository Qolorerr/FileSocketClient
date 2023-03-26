# FileSocket
Library for file transfer and remote PC control

## Links
- [Client GitHub](https://github.com/Qolorerr/FileSocketClient)
- [Server GitHub](https://github.com/Qolorerr/FileSocketServer) - Client needs it to establish connection to PC

## Quick usage
```python
from pathlib import Path
from filesocket import sign_in, show_all_pc, ManagedClient, ManagingClient


# Sign in
sign_in("login", "password")

# Create managed client
client = ManagedClient(port=7999, require_token='token')
client.run()

# Get managed pc id
all_pc = show_all_pc()

# Create managing client
client = ManagingClient(device_id=all_pc[0].id, device_secure_token='token')
client.run(text_ui=False)

# Send cmd command
client.cmd_command('ipconfig')

# Send file
client.send_file(Path("local/path/to/file/to/send"), Path("path/where/to/put"))
```
