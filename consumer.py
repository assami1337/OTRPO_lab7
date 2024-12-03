import asyncio
import os
from aiohttp import ClientSession
from aio_pika import connect_robust, Message
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")


async def fetch_links(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                links = []
                for a_tag in soup.find_all("a", href=True):
                    href = urljoin(url, a_tag["href"])
                    if urlparse(href).netloc == urlparse(url).netloc:
                        links.append((a_tag.get_text(strip=True), href))
                return links
    return []


async def consumer():
    connection = await connect_robust(
        host=os.getenv("RABBITMQ_HOST"),
        port=int(os.getenv("RABBITMQ_PORT")),
        login=os.getenv("RABBITMQ_USER"),
        password=os.getenv("RABBITMQ_PASSWORD"),
    )
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(RABBITMQ_QUEUE)

        try:
            async with queue.iterator(timeout=10) as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        url = message.body.decode()
                        print(f"Обрабатывается: {url}")
                        links = await fetch_links(url)
                        for title, link in links:
                            print(f"Найдена ссылка: {title} - {link}")
                            new_message = Message(link.encode())
                            await channel.default_exchange.publish(new_message, routing_key=RABBITMQ_QUEUE)
        except asyncio.exceptions.TimeoutError:
            print("Очередь пуста. Завершение работы.")

if __name__ == "__main__":
    asyncio.run(consumer())
