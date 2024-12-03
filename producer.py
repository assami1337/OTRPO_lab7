import asyncio
import os
from aiohttp import ClientSession
from aio_pika import connect_robust, Message
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")

async def fetch_links(url):
    """Извлекает внутренние ссылки с указанного URL."""
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                links = []
                for a_tag in soup.find_all("a", href=True):
                    href = urljoin(url, a_tag["href"])
                    if urlparse(href).netloc == urlparse(url).netloc:  # Только внутренние ссылки
                        links.append((a_tag.get_text(strip=True), href))
                return links
    return []

async def producer():
    """Парсит ссылки и отправляет их в очередь RabbitMQ."""
    url = input("Введите URL для обработки: ").strip()
    links = await fetch_links(url)

    connection = await connect_robust(
        host=os.getenv("RABBITMQ_HOST"),
        port=int(os.getenv("RABBITMQ_PORT")),
        login=os.getenv("RABBITMQ_USER"),
        password=os.getenv("RABBITMQ_PASSWORD")
    )
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(RABBITMQ_QUEUE)

        for title, link in links:
            print(f"Добавлено в очередь: {title} - {link}")
            message = Message(link.encode())
            await channel.default_exchange.publish(message, routing_key=RABBITMQ_QUEUE)

if __name__ == "__main__":
    asyncio.run(producer())
