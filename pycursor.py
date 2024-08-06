import asyncio
import aiohttp
import pyautogui
from pynput import mouse
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin SDK
cred = credentials.Certificate("C:/Users/jai10/Downloads/mouse-53e0d-firebase-adminsdk-keg1t-59614be5cb.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mouse-53e0d-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Reference to the database path where cursor data will be stored
db_url = 'https://mouse-53e0d-default-rtdb.asia-southeast1.firebasedatabase.app/mouse_data.json'

class MouseMonitor:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.x = 0
        self.y = 0
        self.scroll = (0, 0)
        self.click = None
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
    
    def on_move(self, x, y):
        self.x = x - self.screen_width // 2
        self.y = y - self.screen_height // 2

    def on_click(self, x, y, button, pressed):
        self.click = (button.name, pressed)

    def on_scroll(self, x, y, dx, dy):
        self.scroll = (dx, dy)

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

    def get_data(self):
        return {
            'position': {'x': self.x, 'y': self.y},
            'scroll': {'dx': self.scroll[0], 'dy': self.scroll[1]},
            'click': {'button': self.click[0], 'pressed': self.click[1]} if self.click else None
        }

async def upload_mouse_data(session, monitor):
    while True:
        data = monitor.get_data()
        try:
            async with session.put(db_url, json=data) as response:
                if response.status == 200:
                    print(f'Uploaded mouse data: {data}', end='\r')
                else:
                    print(f'Failed to upload: {response.status}', end='\r')
        except aiohttp.ClientConnectorError as e:
            print(f'Connection error: {e}', end='\r')

        await asyncio.sleep(0.3)

async def main():
    monitor = MouseMonitor()
    monitor.start()
    async with aiohttp.ClientSession() as session:
        await upload_mouse_data(session, monitor)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by the user.")
