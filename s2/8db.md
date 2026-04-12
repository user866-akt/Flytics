MongoDB
```yml
services:
  mongodb:
    image: mongo:8
    environment:
      - MONGO_INITDB_ROOT_USERNAME=root
      - MONGO_INITDB_ROOT_PASSWORD=root
    ports:
      - "27017:27017"
    volumes:
      - mongodb-data:/data/db
    networks:
      - mongodb-network

volumes:
  mongodb-data:

networks:
  mongodb-network:
    driver: bridge
```
```javascript
use shop_db
db.users.insertMany([
    {
        name: "Иван Петров",
        email: "ivan@mail.ru",
        age: 28,
        city: "Москва",
        registeredAt: new Date("2023-01-15")
    },
    {
        name: "Анна Сидорова",
        email: "anna@mail.ru",
        age: 34,
        city: "Санкт-Петербург",
        registeredAt: new Date("2023-06-20")
    },
    {
        name: "Петр Иванов",
        email: "petr@mail.ru",
        age: 41,
        city: "Казань",
        registeredAt: new Date("2024-01-10")
    }
])
var user1 = db.users.findOne({email: "ivan@mail.ru"})._id
var user2 = db.users.findOne({email: "anna@mail.ru"})._id
var user3 = db.users.findOne({email: "petr@mail.ru"})._id
db.products.insertMany([
    {
        name: "Ноутбук Apple MacBook Pro 14",
        price: 189990,
        category: "Электроника",
        specifications: {
            cpu: "M3 Pro",
            ram: "18GB",
            ssd: "512GB",
            screen: "14.2 Liquid Retina XDR"
        },
        reviews: [
            { user: "user_ivan", rating: 5, comment: "Отличный экран!" },
            { user: "user_petr", rating: 4, comment: "Мощный, но дорогой" }
        ],
        tags: ["apple", "профессиональный", "новинка"],
        in_stock: true
    },
    {
        name: "Смартфон Samsung Galaxy S24",
        price: 89990,
        category: "Электроника",
        specifications: {
            cpu: "Snapdragon 8 Gen 3",
            ram: "8GB",
            storage: "256GB",
            camera: "50MP"
        },
        reviews: [
            { user: "anna_s", rating: 5, comment: "Шикарный дизайн" }
        ],
        tags: ["samsung", "android", "флагман"],
        in_stock: true
    },
    {
        name: "Наушники Sony WH-1000XM5",
        price: 29990,
        category: "Аудио",
        specifications: {
            type: "Bluetooth",
            noise_cancel: true,
            battery_life: "30 hours"
        },
        reviews: [],
        tags: ["sony", "наушники", "шумоподавление"],
        in_stock: false
    }
])
var macbook = db.products.findOne({name: "Ноутбук Apple MacBook Pro 14"})._id
var samsung = db.products.findOne({name: "Смартфон Samsung Galaxy S24"})._id
var sony = db.products.findOne({name: "Наушники Sony WH-1000XM5"})._id
var macbookPrice = db.products.findOne({name: "Ноутбук Apple MacBook Pro 14"}).price
var samsungPrice = db.products.findOne({name: "Смартфон Samsung Galaxy S24"}).price
var sonyPrice = db.products.findOne({name: "Наушники Sony WH-1000XM5"}).price
db.orders.insertMany([
    {
        userId: user1,
        productIds: [macbook],
        totalAmount: macbookPrice,
        status: "delivered",
        orderDate: new Date("2024-02-10")
    },
    {
        userId: user2,
        productIds: [samsung],
        totalAmount: samsungPrice,
        status: "processing",
        orderDate: new Date("2024-03-15")
    },
    {
        userId: user1,
        productIds: [macbook, samsung],
        totalAmount: macbookPrice + samsungPrice,
        status: "pending",
        orderDate: new Date("2024-03-20")
    },
    {
        userId: user3,
        productIds: [sony],
        totalAmount: sonyPrice,
        status: "cancelled",
        orderDate: new Date("2024-03-01")
    }
])
```
![](images/img98.png)
![](images/img99.png)
![](images/img100.png)
![](images/img101.png)
![](images/img102.png)
